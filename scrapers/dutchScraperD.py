import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from model.dutchDetector import DutchDetector
import time, re

START_URLS = [ "https://www.nu.nl", "https://nl.wikipedia.org" ]
SPIDER_NAME = "dataSpider"
TRUST_FACTOR = 0.1 # 0.1 means 10% less likely to be dutch is fine considered dutch aswell.
PERIOD_OF_TIME = 3600

def filterTrailingBackslash(url):
    if (url.endswith('/')):
        return url[:-1]
    else:
        return url

def filterMediaQueries(url):
    res = re.search("(.*?)\?", url)
    if res:
        return res[1]
    else:
        return url

filterUrl = lambda x: filterTrailingBackslash(filterMediaQueries(x))
start_time = time.time()

class DataSpider(scrapy.Spider):
    name = SPIDER_NAME
    start_urls = START_URLS
    link_extractor = LinkExtractor(restrict_css = "body", unique = True, process_value=filterUrl)
    detector = DutchDetector()
    
    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'DNS_TIMEOUT': 10
    }

    def urlIsDutch(self, url, trust):
        percentage = self.detector.isDutchPercentage(url)
        if (trust >= 1):
            return percentage > 0.5 - TRUST_FACTOR
        else:
            return percentage > 0.5
    
    def parseLink(self, response, trust=1):
        if (time.time() > start_time + PERIOD_OF_TIME):
            raise CloseSpider("Time limit reached")
        if (trust >= 1):
            yield { "url": response.url }

        links = self.link_extractor.extract_links(response)
        leftOverLinks = []

        for link in links:
            if self.urlIsDutch(link.url, trust):
                yield scrapy.Request(link.url, priority=trust, callback=lambda x: self.parseLink(x, trust + 1))
            else:
                leftOverLinks.append(link)

        for leftOverLink in leftOverLinks:
            yield scrapy.Request(leftOverLink.url, priority=0, callback=lambda x: self.parseLink(x, 0))

    def parse(self, response):
        return self.parseLink(response, 1)

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
import time, re

START_URLS = [ "https://www.nu.nl", "https://nl.wikipedia.org" ]
SPIDER_NAME = "dataSpider"
PERIOD_OF_TIME = 3600

def getTopLevelDomain(url):
    parts = url.split("/")[2].split(".")
    return parts[len(parts)-1]

def urlIsDutch(url):
    topLevelDomain = getTopLevelDomain(url).lower()
    if (topLevelDomain == 'nl' or topLevelDomain == 'sr'):
        return True
    return False

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

    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'DNS_TIMEOUT': 10
    }
    
    def parseLink(self, response, trust=1):
        if (time.time() > start_time + PERIOD_OF_TIME):
            raise CloseSpider("Time limit reached")
        if (trust >= 1):
            yield { "url": response.url }

        links = self.link_extractor.extract_links(response)
        leftOverLinks = []

        for link in links:
            if urlIsDutch(link.url):
                yield scrapy.Request(link.url, priority=trust, callback=lambda x: self.parseLink(x, trust + 1))
            else:
                leftOverLinks.append(link)

        for leftOverLink in leftOverLinks:
            yield scrapy.Request(leftOverLink.url, priority=0, callback=lambda x: self.parseLink(x, 0))

    def parse(self, response):
        return self.parseLink(response, 1)

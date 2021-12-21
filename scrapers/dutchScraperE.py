import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from langdetect import detect
from model.dutchDetector import DutchDetector
import time, re
import w3lib.html

START_URLS = [ "https://www.nu.nl", "https://nl.wikipedia.org" ]
SPIDER_NAME = "dataSpider"
SAMPLES = 1
TAG_LIST = ['p', 'section', 'div', 'span', 'h3', 'h2', 'h1', 'a']
PERIOD_OF_TIME = 3600

filterNonWords = lambda x: " ".join(re.findall("[a-zA-Z]+", x))

def sampleIsDutch(sample):
    code = detect(sample)
    return 'nl' == code

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
    
    def parseLink(self, response, trust=1):
        if (time.time() > start_time + PERIOD_OF_TIME):
            raise CloseSpider("Time limit reached")

        links = self.link_extractor.extract_links(response)

        newTrust = trust + 1
        if (self.detector.isDutch(response.url)):
            yield { "url": response.url }
        else:
            newTrust = 0

        for link in links:
            yield scrapy.Request(link.url, priority=newTrust, callback=lambda x: self.parseLink(x, newTrust))

    def parse(self, response):
        return self.parseLink(response, 1)

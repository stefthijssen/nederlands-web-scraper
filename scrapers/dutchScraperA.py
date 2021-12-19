import scrapy
from scrapy.linkextractors import LinkExtractor
import re

START_URLS = [ "https://waarneming.nl", "https://www.nu.nl", "https://nl.wikipedia.org" ]
SPIDER_NAME = "dataSpider"

def getTopLevelDomain(url):
    parts = url.split("/")[2].split(".")
    return parts[len(parts)-1]

def urlIsDutch(url):
    topLevelDomain = getTopLevelDomain(url).lower()
    if (topLevelDomain == 'nl' or topLevelDomain == 'sr'):
        return True
    return False

def filterMediaQueries(url):
    res = re.search("(.*?)\?", url)
    if res:
        return res[1]
    else:
        return url


class DataSpider(scrapy.Spider):
    name = SPIDER_NAME
    start_urls = START_URLS
    link_extractor = LinkExtractor(restrict_css = "body", unique = True, process_value=filterMediaQueries)

    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'DNS_TIMEOUT': 10
    }
    
    def parseLink(self, response, trust=1):
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

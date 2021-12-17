import scrapy
from scrapy.linkextractors import LinkExtractor
from expirimentalMethods import fC

START_URLS = [ "https://www.nu.nl", "https://nl.wikipedia.org" ]
SPIDER_NAME = "dataSpider"

urlIsDutch = fC

class DataSpider(scrapy.Spider):
    name = SPIDER_NAME
    start_urls = START_URLS
    link_extractor = LinkExtractor(restrict_css = "body", unique = True)

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

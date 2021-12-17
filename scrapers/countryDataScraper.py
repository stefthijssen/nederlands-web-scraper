import scrapy
import inspect
import re
import w3lib.html

START_URL = "https://curlie.org/af"
SPIDER_NAME = "dataSpider"
DOCUMENT_HREF_SELECTOR = "section.sites div.title-and-desc a::attr(href)"
SAMPLES = 5
TAG_LIST = ['p', 'h1', 'h2', 'a', 'span', 'div']

filterNonWords = lambda x: " ".join(re.findall("[a-zA-Z]+", x))

class DataSpider(scrapy.Spider):
    name = SPIDER_NAME
    start_urls = [ START_URL ]

    custom_settings = {
        'LOG_LEVEL': 'ERROR',
        'DNS_TIMEOUT': 10
    }

    def removeHtmlTags(self, string):
        return w3lib.html.remove_tags(string)

    def removeWhitespace(self, string):
        return " ".join(string.split())

    def htmlElementToCleanText(self, el):
        return self.removeWhitespace(self.removeHtmlTags(el.get()))

    def getHtmlElementsAsText(self, selector, response):
        htmlElements = response.css(selector)
        textList = map(filterNonWords, map(self.htmlElementToCleanText, htmlElements))
        return list(filter(None, textList))

    def getSamples(self, foundSamples, tagListIndex, response):
        if len(foundSamples) >= SAMPLES or tagListIndex >= len(TAG_LIST):
            return foundSamples
        else:
            ls = self.getHtmlElementsAsText(TAG_LIST[tagListIndex], response)
            samplesToFindLeft = SAMPLES - len(foundSamples)
            newFoundSamples = foundSamples
            if len(ls) >= samplesToFindLeft:
                newFoundSamples += ls[0:samplesToFindLeft]
            elif len(ls) != 0:
                newFoundSamples += ls
            return self.getSamples(newFoundSamples, tagListIndex + 1, response)


    def getClassificationSentences(self, response):
        return self.getSamples([], 0, response)

    def parse(self, response):
        if not response.url.startswith(START_URL):
            samples = self.getClassificationSentences(response)
            if (len(samples) != 0):
                yield {
                    "siteUrl": response.url,
                    "sample": samples
                }
        else:
            hrefs = list(map(lambda x: response.urljoin(x), response.css('a::attr(href)').extract()))
            dutchHrefs = list(filter(lambda x : x.startswith(START_URL), hrefs))
            documentHrefs = response.css(DOCUMENT_HREF_SELECTOR).extract()

            for href in documentHrefs:
                yield scrapy.Request(href, callback=self.parse)

            for href in dutchHrefs:
                yield scrapy.Request(href, callback=self.parse)
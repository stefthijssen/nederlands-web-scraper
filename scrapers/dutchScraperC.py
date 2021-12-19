import scrapy
from scrapy.linkextractors import LinkExtractor
from langdetect import detect
from model.dutchDetector import DutchDetector
import re
import w3lib.html

START_URLS = [ "https://www.nu.nl", "https://nl.wikipedia.org" ]
SPIDER_NAME = "dataSpider"
SAMPLES = 1
TAG_LIST = ['p', 'section', 'div', 'span', 'h3', 'h2', 'h1', 'a']

filterNonWords = lambda x: " ".join(re.findall("[a-zA-Z]+", x))

detector = DutchDetector()

def urlIsDutch(url):
    return detector.isDutch(url)

def sampleIsDutch(sample):
    code = detect(sample)
    return 'nl' == code
class DataSpider(scrapy.Spider):
    name = SPIDER_NAME
    start_urls = START_URLS
    link_extractor = LinkExtractor(restrict_css = "body", unique = True)

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
    
    def parseLink(self, response, trust=1):
        if (trust >= 1):
            yield { "url": response.url }

        links = self.link_extractor.extract_links(response)
        leftOverLinks = []

        for link in links:
            if urlIsDutch(link.url):
                sample = self.getClassificationSentences()[0]
                if sampleIsDutch(sample):
                    yield scrapy.Request(link.url, priority=trust, callback=lambda x: self.parseLink(x, trust + 1))
            else:
                leftOverLinks.append(link)

        for leftOverLink in leftOverLinks:
            yield scrapy.Request(leftOverLink.url, priority=0, callback=lambda x: self.parseLink(x, 0))

    def parse(self, response):
        return self.parseLink(response, 1)

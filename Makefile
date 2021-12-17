test: 
	timeout --foreground 1h make run

run:
	scrapy runspider scrapers/dutchScraper.py -o out.json
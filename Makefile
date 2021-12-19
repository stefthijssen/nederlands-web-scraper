test: 
	timeout --foreground 1h make run

run:
	scrapy runspider scrapers/dutchScraperA.py -o testA.json
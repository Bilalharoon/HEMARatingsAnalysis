from scraper import HEMARatingsScraper

web_scraper = HEMARatingsScraper()

history = web_scraper.get_match_history(711)
print(history)

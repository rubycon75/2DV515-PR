"""
Run to create new dataset.
"""
from wikiscraper import WikiScraper

print("Enter name of article to make dataset from:")
PAGE = input("> ")

WS = WikiScraper()
WS.init_dataset(PAGE)
WS.create_dataset()

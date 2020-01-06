"""
WikiScraper module.
"""
import re
import os
import time
from contextlib import closing
from requests import get
from bs4 import BeautifulSoup as bs

class WikiScraper:
    """
    WikiScraper class.
    Downloads pages from wikipedia, formats them and creates a dataset.

    Attributes:
        title (str): page title to build dataset from
        base_url (str): wikipedia base url
    """
    title = None
    base_url = "https://en.wikipedia.org/"

    def init_dataset(self, title):
        """
        Set wiki page to create dataset and start scraping from,
        create unneccessary folders.

        Args:
            title (str): title of wiki page

        Raises:
            FileExistsError: dataset already exists
        """
        # store page title to scrape from
        self.title = "wiki/" + title

        if not os.path.isdir("./datasets"):
            # create /datasets dir if it doesn't exist
            os.mkdir("./datasets")

        if os.path.isdir("./datasets/" + title):
            # raise exception if dataset for given page already exists
            raise FileExistsError("Dataset already exists.")
        else:
            # create dirs for dataset
            os.mkdir("./datasets/" + title)
            os.mkdir("./datasets/" + title + "/Words")
            os.mkdir("./datasets/" + title + "/Links")

    def download_page(self, url):
        """
        Downloads webpage and returns the raw html data.

        Args:
            url (str): url for webpage

        Returns:
            str: raw html data
        """
        with closing(get(url, stream=True)) as resp:
            # decode bytes object to string
            html = resp.content.decode("utf-8")
            return html

    def try_decompose(self, soup, el, attr):
        """
        Try to delete part of soup object, pass if exception is raised.

        Args:
            soup: object
            el (str): element
            attr (dict): attribute/value
        """
        try:
            soup.find(el, attr).decompose()
        except:
            pass

    def get_and_parse_page(self, page):
        """
        Download html data, clean up unwanted elements and return formatted
        text and list of outgoing links.

        Args:
            page (url): url/name of page (should be 'wiki/title' format)

        Returns:
            list: title, text and outgoing links
        """
        # get raw html
        html = self.download_page(self.base_url + page)

        # remove unneccessary parts of html
        start = html.find("<div class=\"mw-parser-output\">")
        notes = html.find("<span class=\"mw-headline\" id=\"Notes\">")
        refs = html.find("<span class=\"mw-headline\" id=\"References\">")
        nr = [notes, refs]
        end = min(nr) if -1 not in nr else max(nr)
        end = end if end is not -1 else 100000000
        html = html[start:end]

        # create beautifulsoup object
        soup = bs(html, 'html.parser')

        # remove unneccessary notes
        for note in soup.findAll("div", {"class": "hatnote"}):
            if note.findAll(text=re.compile('This article is about')):
                note.decompose()
            if note.findAll(text=re.compile('redirects here')):
                note.decompose()
            if note.findAll(text=re.compile('(disambiguation)')):
                note.decompose()
            if note.findAll(text=re.compile('Not to be confused')):
                note.decompose()

        # remove table of contents
        self.try_decompose(soup, "div", {"id": "toc"})

        # remove infobox
        self.try_decompose(soup, "table", {"class": "infobox"})

        # remove short description
        self.try_decompose(soup, "div", {"class": "shortdescription"})

        # remove unneccessary boxes
        for table in soup.findAll("table", {"class": "ambox"}):
            table.decompose()

        # remove style tags
        for style in soup.findAll("style"):
            style.decompose()

        # get text
        text = soup.get_text().lower().strip()

        # remove brackets and content
        text = re.sub(r'\[.*?\]', '', text)

        # remove all characters but letters
        text = re.sub(r"[^a-zA-Z0-9]+", ' ', text)

        # get outgoing links
        links = soup.findAll('a')
        linkset = set()
        for l in links:
            link = l.get("href")
            try:
                if link[:6] == "/wiki/":
                    # remove unwanted links
                    if link[6:11] in ["File:", "Help:"]:
                        continue
                    if link[6:13] == "Portal:":
                        continue
                    if link[6:14] == "Special:":
                        continue
                    if link[6:16] == "Wikipedia:":
                        continue
                    if "/" in link[6:]:
                        continue
                    # shorten links which include a '#'
                    if link.find("#") != -1:
                        link = link[:link.find("#")]
                    # add link to set
                    linkset.add(link)
            except:
                pass

        # return dict with title, text and outgoing links
        return {"text": text, "links": linkset, "title": page[5:]}

    def save_page(self, data):
        """
        Save text and links from page in separate files.

        Args:
            data (dict): title, text and outgoing links for page
        """
        # get dataset dir
        working_dir = os.path.dirname(os.path.realpath(__file__))
        ds = working_dir + "/datasets/" + self.title[5:]

        # save text file
        f = open(ds + "/Words/" + data["title"], "w")
        f.write(data["text"])
        f.close()

        # save links file
        f = open(ds + "/Links/" + data["title"], "w")
        f.write('\n'.join(data["links"]))
        f.close()

    def create_dataset(self):
        """
        Downloads first page, then downloads all outgoing links
        and creates a dataset.

        Raises:
            RunTimeError: no dataset initiated
        """
        if self.title is None:
            # raise exception if dataset is not initiated
            raise RunTimeError("No dataset initiated.")

        # start timer
        start = time.time()

        # get first page and save files
        first = self.get_and_parse_page(self.title)
        link_amount = len(first["links"])
        self.save_page(first)

        # print info
        print("Downloaded page: " + self.base_url + self.title)
        print("Outgoing links: " + str(link_amount))
        print("---")

        # download outgoing links
        count = 1
        for l in first["links"]:
            data = self.get_and_parse_page(l)
            self.save_page(data)
            print("Downloaded page {}/{} - {}".format(count, link_amount, l))
            count += 1

        print("---")

        # end timer and print info
        end = time.time()
        print("Dataset of {} pages created in {} seconds.".format(
            link_amount+1,
            round(end-start, 2)))

"""
PageDB module.
"""
import os
import time
from urllib import parse

class PageDB:
    """
    PageDB class.

    Attributes:
        words (dict): dict of words with id numbers used in the pages
        pages (list): list of Page objects
    """
    words = dict()
    pages = list()

    def __init__(self, dataset):
        """
        PageDB constructor.
        Parse data from files, create Page objects, calculate PageRank.

        Args:
            dataset (str): name of dataset to use

        Raises:
            NotADirectoryError: if dataset doesn't exist
        """
        # raise exception if dataset does not exist
        if not os.path.isdir("./datasets/" + dataset):
            raise NotADirectoryError("Dataset not found.")

        print("Creating page object for each page... ")
        start = time.time()
        workingdir = os.path.dirname(os.path.realpath(__file__))
        path = workingdir + "/datasets/" + dataset + "/Words"
        for subdir, dirs, files in os.walk(path):
            for file in files:
                # iterate through files
                filepath = os.path.join(subdir, file)
                with open(filepath, "r") as f:
                    words_temp = f.read().split()
                    word_ints = list()
                    # get integers for all words in file
                    for word in words_temp:
                        word_ints.append(self.get_id_for_word(word))
                links_path = filepath.replace("Words", "Links", 1)
                links = set()
                # get links for each article
                with open(links_path, "r") as f:
                    for line in f.read().split("\n"):
                        if len(line) > 1:
                            links.add(parse.unquote(line[6:]))
                # create Page object for each file
                self.pages.append(Page(parse.unquote(file), word_ints, links))
        end = time.time()
        print("Done in {} seconds.".format(round(end - start, 2)))
        print("Calculating PageRank for each page... ")
        start = time.time()
        i = 0
        max_iterations = 20
        while i < max_iterations:
            ranks = list()
            j = 0
            # calculate pagerank values for all pages
            while j < len(self.pages):
                ranks.append(self.pagerank(self.pages[j]))
                j += 1
            j = 0
            # normalize scores if it is the last iteration
            if i == max_iterations-1:
                self.normalize(ranks, False)
            # set pagerank values for all pages
            while j < len(self.pages):
                self.pages[j].pagerank = ranks[j]
                j += 1
            i += 1
        end = time.time()
        print("Done in {} seconds.".format(round(end - start, 2)))

    def pagerank(self, page):
        """
        Calculate pagerank score for a page.

        Args:
            page (Page): page object

        Returns:
            float: pagerank score
        """
        pr = 0
        # iterate over all pages
        for p in self.pages:
            # check if the other page links to this page
            if page.url in p.links:
                pr += p.pagerank / len(p.links)
        # caluclate and return pagerank
        pr = 0.85 * pr + 0.15
        return pr

    def query(self, query):
        """
        Perform search using query string.

        Args:
            query (string): one or more words to search for

        Returns:
            list: nested list of results sorted by scores
        """
        # init variables
        scores = dict()
        scores["content"] = list()
        scores["location"] = list()
        matches = list()
        result = list()
        # start timer
        start = time.time()
        # convert query string to lowercase and make int list
        query_ints = list()
        for word in query.lower().split():
            query_ints.append(self.get_id_for_word(word))
        # find matching pages
        for page in self.pages:
            for i in query_ints:
                if i in page.words:
                    matches.append(page)
                    break
        # calculate scores for matching pages
        i = 0
        while i < len(matches):
            scores["content"].append(self.word_frequency(matches[i], query_ints))
            scores["location"].append(self.document_location(matches[i], query_ints))
            i += 1
        # normalize scores
        if len(matches) > 0:
            self.normalize(scores["content"], False)
            self.normalize(scores["location"], True)
        # make result list and return sorted
        i = 0
        while i < len(matches):
            res1 = round(scores["content"][i], 2)
            res2 = round(scores["location"][i] * 0.8, 2)
            res3 = round(matches[i].pagerank * 0.5, 2)
            total = round(res1 + res2 + res3, 2)
            result.append([matches[i].url, total, res1, res2, res3])
            i += 1
        amount = len(result)
        end = time.time()
        duration = round(end - start, 2)
        result = sorted(result, key=lambda x: x[1], reverse=True)[:5]
        return {"data": result, "amount": amount, "duration": duration}

    def word_frequency(self, page, query_ints):
        """
        Count occurrances of search words in page and return score.

        Args:
            page (Page): page object
            query_ints (list): list of ints representing words

        Returns:
            int: frequency score
        """
        score = 0
        for q in query_ints:
            score += page.words.count(q)
        return score

    def document_location(self, page, query_ints):
        """
        Check indexes of search words in page and calculate a score.

        Args:
            page (Page): page object
            query_ints (list): list of ints representing words

        Returns:
            int: document location score
        """
        score = 0
        # iterate over each word in the search query
        for w in query_ints:
            try:
                # add index of word to score if found
                score += page.words.index(w) + 1
            except:
                # add large number to score if not found
                score += 100000
        # return result
        return score

    def normalize(self, scores, small_is_better):
        """
        Takes a list of floats and normalizes the scores between 0 and 1.

        Args:
            scores (list): list of floats
            small_is_better (bool): True if small score is better
        """
        if small_is_better:
            # smaller values shall be inverted to higher values
            # and scaled between 0 and 1
            min_val = min(scores)
            i = 0
            while i < len(scores):
                scores[i] = min_val / max(scores[i], 0.00001)
                i += 1
        else:
            # higher values shall be scaled between 0 and 1
            max_val = max(scores)
            max_val = max(max_val, 0.00001)
            i = 0
            while i < len(scores):
                scores[i] = scores[i] / max_val
                i += 1

    def get_id_for_word(self, word):
        """
        Returns ID for a word, and adds the word if not added already.

        Args:
            word (string): word to get ID for

        Returns:
            int: ID for word
        """
        if word in self.words:
            # word found, return id
            return self.words[word]
        # add missing word
        self.words[word] = len(self.words)
        return len(self.words)-1


class Page:
    """
    Page class.

    url (string): url to the page
    words (list): integers presenting words
    links (list): outgoing links from page
    pagerank (float) : pagerank score
    """

    def __init__(self, url, words, links):
        """
        Page constructor.
        Sets attributes.

        Args:
            url (string): url to page
            words (list): integers presenting words
            links (list): outgoing links from page
        """
        self.url = url
        self.words = words
        self.links = links
        self.pagerank = 1.0

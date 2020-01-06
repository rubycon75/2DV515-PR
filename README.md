# 2DV515-PR
Project in 2DV515 Web Intelligence.  
Web scraping for wikipedia articles + search engine from assignment 3.  
Requirements: Python 3.6+ and modules *flask*, *flask-cors*, *requests*, *BeautifulSoup4*  

## How to run
*Web scraping:* Run create_dataset.py and enter name of Wikipedia article.  
*Search enginge:* Run server.py to start the server at localhost:5000, open client.html in a browser.

## API routes

### GET /{query}
{query} must be a string of one or more words.
Returns an object including info about duration and amount of hits, as well as an array of results.

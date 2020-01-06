"""
2DV515 Web Intelligence
Project- Web Scraping
by David Johansson (dj222dq)
"""

from flask import Flask, jsonify
from flask_cors import CORS
from pagedb import PageDB

# name of dataset to use
dataset = "Electric_guitar"

APP = Flask(__name__)
PAGEDB = PageDB(dataset)

CORS(APP)

@APP.route('/<string:search_term>')
def search(search_term):
    return jsonify(PAGEDB.query(search_term))

if __name__ == "__main__":
    APP.run()

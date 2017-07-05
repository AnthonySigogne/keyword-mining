#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API - extract keywords from a text.

The algorithm extracts the main nominal groups (relevant keyword candidates) from the text
and, for each one, attributes a score based on multiple parameters including the number of occurrences.
"""

__author__ = "Anthony Sigogne"
__copyright__ = "Copyright 2017, Byprog"
__email__ = "anthony@byprog.com"
__license__ = "MIT"
__version__ = "1.0"

# libraries of tool
import url
import language
from flask import Flask, request, jsonify

# init flask app and import helper
app = Flask(__name__)
with app.app_context():
    from helper import *

@app.route("/keywords_from_text", methods=['POST'])
def keywords_from_text():
    """
    URL : /keywords_from_text
    Extract keywords from a text.
    Method : POST
    Form data :
        - text : the text to analyze [string, required]
        - hits : limit number of keywords returned [int, optional, 100 by default]
    Return a JSON dictionary : {"keywords":[list of keywords]}
    """
    # get POST data and load language resources
    data = dict((key, request.form.get(key)) for key in request.form.keys())
    if "text" not in data :
        raise InvalidUsage('No text specified in POST data')

    # detect main language and extract keywords
    keywords = language.keyword_mining(data["text"])

    # limit the number of keywords
    total = len(keywords)
    hits = int(data.get("hits", 100))
    keywords = [kw for kw, score in keywords.most_common(hits)]
    return jsonify(keywords=keywords, total=total)

@app.route("/keywords_from_url", methods=['POST'])
def keywords_from_url():
    """
    URL : /keywords_from_url
    Extract keywords from the text content of a web page.
    Method : POST
    Form data :
        - url : the url to analyze [string, required]
        - hits : limit number of keywords returned [int, optional, 100 by default]
    Return a JSON dictionary : {"keywords":[list of keywords]}
    """
    # get POST data and load language resources
    data = dict((key, request.form.get(key)) for key in request.form.keys())
    if "url" not in data :
        raise InvalidUsage('No url specified in POST data')

    # crawl url, detect main language and get main text from url
    url_data = url.crawl(data["url"])
    if not url_data :
        raise InvalidUsage('No content to analyze')
    text_content = url.extract_content(url_data.text)

    # analyze text and extract keywords
    keywords = language.keyword_mining(text_content)

    # limit the number of keywords
    total = len(keywords)
    hits = int(data.get("hits", 100))
    keywords = [kw for kw, score in keywords.most_common(hits)]
    return jsonify(keywords=keywords, total=total)

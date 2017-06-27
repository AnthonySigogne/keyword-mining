#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API to extract keywords from a text.
The algorithm extracts the main nominal groups (relevant keywords) from the text and, for each one,
attributes a score based on multiple parameters including the number of occurrences.
"""

__author__ = "Anthony Sigogne"
__copyright__ = "Copyright 2017, Byprog"
__email__ = "anthony@byprog.com"
__license__ = "MIT"
__version__ = "1.0"

# libraries of tool
import justext
import requests
from collections import Counter
from pattern.search import search, match
from flask import Flask, request, jsonify, url_for, render_template
app = Flask(__name__)

@app.route("/keywords", methods=['POST'])
def keyword_mining_text():
    """
    URL : /keywords
    Extract keywords from a text.
    Method : POST
    Form data :
        - text : the text to analyze
        - language : language of text ("fr" or "en")
    Return a JSON dictionary : {"keywords":[list of keywords]}
    """
    # get POST data and load language resources
    data = dict((key, request.form.get(key)) for key in request.form.keys())
    if "text" not in data :
        raise InvalidUsage('No text specified in POST data')
    load_resources(data)

    # analyze text and extract keywords
    keyword_mining(data)

    # get only the 15 best scored keywords
    keywords = [kw for kw, score in data["keywords"].most_common(15)]
    return jsonify(keywords=keywords)

@app.route("/keywords_at_url", methods=['POST'])
def keyword_mining_url():
    """
    URL : /keywords_at_url
    Extract keywords from the text of a web page.
    Method : POST
    Form data :
        - url : the url to analyze
        - language : language of text ("fr" or "en")
    Return a JSON dictionary : {"keywords":[list of keywords]}
    """
    def crawl_url(data) :
        """
        Crawl url and extract main text content (no boilerplate).
        """
        r = requests.get(data["url"])
        paragraphs = justext.justext(r.text, justext.get_stoplist("French" if data["language"] == "fr" else "English"))
        main_content = ". ".join([paragraph.text for paragraph in paragraphs if not paragraph.is_boilerplate])
        data["text"] = main_content

    # get POST data and load language resources
    data = dict((key, request.form.get(key)) for key in request.form.keys())
    if "url" not in data :
        raise InvalidUsage('No url specified in POST data')
    load_resources(data)

    # get main text from url
    crawl_url(data)

    # analyze text and extract keywords
    keyword_mining(data)

    # get only the 15 best scored keywords
    keywords = [kw for kw, score in data["keywords"].most_common(15)]
    return jsonify(keywords=keywords)

def keyword_mining(data) :
    """
    Extract keywords from a text.
    """
    # tag text
    data["text_tagged"] = data["parse"](data["text"].replace("\n",".\n").replace(u"»"," ").replace(u"«"," ").replace("["," "), relations=True, lemmata=True)
    t = data["tree"](data["text_tagged"])

    # first, extract all keywords
    keywords = Counter()
    GN = {
        "fr":['CD? NN|NNS|NNP+ IN NN|NNS|NNP+ JJ','NN|CD? NN|NNS|NNP+ IN NN|NNS|NNP+','NNP+','NN|NNS|NNP+ JJ'],
        "en":['NN|NNS|NNP+ IN JJ NN|NNS|NNP','NN|NNS|NNP+ IN NN|NNS|NNP+','NNP+','JJ NN|NNS|NNP+','NN VBG NN']
    }
    for p in GN[data["language"]] :
        for match in search(p, t):
            if "@" in match.string or ";" in match.string or match.string.count(" ") > 6 :
                continue
            keywords[match.string] += match.string.count(" ")+1

    # then, filter keywords (keywords in another are removed)
    for kw,v in keywords.items() :
        for kw2,v2 in keywords.items() :
            if kw != kw2 and kw.lower() in kw2.lower() and v2 >= v:
                keywords[kw2] += 1
                del keywords[kw]
    data["keywords"] = keywords

def load_resources(data) :
    """
    Load linguistic resources for a language.
    """
    if "language" not in data :
        raise InvalidUsage('No language specified in POST data')
    if data["language"] == "fr" :
        from pattern.fr import parse, tree, ngrams
    elif data["language"] == "en" :
        from pattern.en import parse, tree, ngrams
    else :
        raise InvalidUsage('Unsupported language')
    data.update({
        "parse" : parse,
        "tree" : tree,
        "ngrams" : ngrams
    })


# -- HELPER AND MISC -- #

@app.route("/")
def helper():
    """
    URL : /
    Helper that list all services of API.
    """
    # print module docstring
    output = [__doc__.replace("\n","<br/>"),]

    # then, get and print docstring of each rule
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static" : # skip static endpoint
            continue
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        output.append(app.view_functions[rule.endpoint].__doc__.replace("\n","<br/>"))

    return "<br/>".join(output)

class InvalidUsage(Exception):
    """
    Custom invalid usage exception.
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    JSON version of invalid usage exception
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API to extract keywords from a text.
The algorithm extracts the main nominal groups (relevant keywords) and, for each one,
attribute a score based on multiple parameters including the number of occurrences.
"""

__author__ = "Anthony Sigogne"
__copyright__ = "Copyright 2017, Byprog"
__email__ = "anthony@byprog.com"
__license__ = "MIT"
__version__ = "1.0"

# libraries of tool
from collections import Counter
from pattern.search import search,match
from flask import Flask, request, jsonify, url_for, render_template
app = Flask(__name__)

def load_resources(data) :
    """
    Load linguistic resources for a language.
    """
    if data["language"] == "fr" :
        from pattern.fr import parse, tree, ngrams
    elif data["language"] == "en" :
        from pattern.en import parse, tree, ngrams
    elif data["language"] == "es" :
        from pattern.es import parse, tree, ngrams
    elif data["language"] == "de" :
        from pattern.de import parse, tree, ngrams
    elif data["language"] == "it" :
        from pattern.it import parse, tree, ngrams
    elif data["language"] == "nl" :
        from pattern.nl import parse, tree, ngrams
    return parse, tree, ngrams

@app.route("/keywords", methods=['POST'])
def keyword_mining():
    """
    URL : /keywords
    Extract keywords from a text.
    Method : POST
    Form data :
        - text : the text to analyze
        - lang : language of text ("fr" or "en")
    Return a JSON dictionary : {"keywords":[list of keywords]}
    """
    # get POST data and load language resources
    data = dict((key, request.form.get(key)) for key in request.form.keys())
    parse, tree, ngrams = load_resources(data)

    # tag text
    data["text_tagged"] = parse(data["text"].replace("\n",".\n").replace(u"»"," ").replace(u"«"," "), relations=True, lemmata=True)
    t = tree(data["text_tagged"])

    # extract keywords
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

    # filter keywords (keywords in another are removed)
    for kw,v in keywords.items() :
        for kw2,v2 in keywords.items() :
            if kw != kw2 and kw in kw2 :
                keywords[kw2] += 1
                del keywords[kw]

    # return the final list of keywords
    return jsonify(keywords=keywords.keys())

@app.route("/")
def helper():
    """
    URL : /
    Helper that list all methods of tool.
    Return a simple text.
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

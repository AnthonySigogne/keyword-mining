#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Toolbox for languages.
"""

__author__ = "Anthony Sigogne"
__copyright__ = "Copyright 2017, Byprog"
__email__ = "anthony@byprog.com"
__license__ = "MIT"
__version__ = "1.0"

import langdetect
from collections import Counter
from pattern.search import search, match

# declare a dictionary of languages (code -> long form)
languages = {
    "fr": "french",
    "en": "english",
    "de": "german",
    "ro": "romanian",
    "ru": "russian",
    "ar": "arabic",
    "hi": "hindi",
    "es": "spanish",
    "fi": "finnish",
    "nl": "dutch",
    "cs": "czech",
    "ca": "catalan",
    "bg": "bulgarian",
    "pt": "portuguese",
    "da": "danish",
    "no": "norwegian",
    "sv": "swedish",
    "el": "greek",
    "th": "thai",
    "tr": "turkish",
    "it": "italian",
    "ga": "irish",
    "hu": "hungarian",
    "lt": "lithuanian",
    "id": "indonesian",
    "fa": "persian",
    "lv": "latvian"
}

def keyword_mining(text) :
    """
    Extract keywords from a text.
    """
    # detect language and load language resources
    lang = langdetect.detect(text)
    if lang == "fr" :
        from pattern.fr import parse, tree
    elif lang == "en" :
        from pattern.en import parse, tree
    else :
        raise InvalidUsage('Unsupported language')

    # tag text
    tagged_text = parse(text.replace("\n",".\n").replace(u"»"," ").replace(u"«"," ").replace("["," "), relations=True, lemmata=True)
    t = tree(tagged_text)

    # first, extract all keywords
    keywords = Counter()
    GN = {
        "fr":['CD? NN|NNS|NNP+ IN NN|NNS|NNP+ JJ','NN|CD? NN|NNS|NNP+ IN NN|NNS|NNP+','NNP+','NN|NNS|NNP+ JJ'],
        "en":['NN|NNS|NNP+ IN JJ NN|NNS|NNP','NN|NNS|NNP+ IN NN|NNS|NNP+','NNP+','JJ NN|NNS|NNP+','NN VBG NN']
    }
    for p in GN[lang] :
        for match in search(p, t):
            gn = match.string
            if not gn.replace(" ","").isalpha() or gn.count(" ") > 6 :
                continue
            keywords[match.string] += match.string.count(" ")+1

    # then, improve score of long-term keywords
    for kw,v in keywords.items() :
        for kw2,v2 in keywords.items() :
            if kw != kw2 and kw.lower() in kw2.lower() and v2 >= v:
                keywords[kw2] += 1
                #del keywords[kw]

    return keywords

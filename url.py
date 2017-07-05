#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Toolbox for URLs.
"""

__author__ = "Anthony Sigogne"
__copyright__ = "Copyright 2017, Byprog"
__email__ = "anthony@byprog.com"
__license__ = "MIT"
__version__ = "1.0"

import re
import langdetect
import html2text
import requests
from HTMLParser import HTMLParser

def crawl(url) :
    """
    Crawl an URL.
    Return URL data.
    """
    try :
        r = requests.get(url)
    except :
        return None
    return r

def extract_content(html) :
    """
    Extract the main text content of a page.
    """
    h = html2text.HTML2Text()
    return h.handle(html)

def extract_title(html) :
    """
    Extract the title of a page.
    """
    h = HTMLParser()
    try :
        title = h.unescape(re.search("<title>([^<]+)</title>", html).group(1))
    except :
        title = "" # no title on page
    return title

def extract_description(html) :
    """
    Extract the description of a page.
    """
    h = HTMLParser()
    try :
        description = h.unescape(re.search('<meta name="[^">]*description"[^">]*content="([^">]+)',html).group(1))
    except :
        description = "" # no description on page
    return description

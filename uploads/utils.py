from __future__ import print_function, unicode_literals, division, absolute_import
from difflib import SequenceMatcher
import logging
import string
import sys

try:
    from bs4 import BeautifulSoup
except ImportError:
    logging.critical('You must install "beautifulsoup4" for this script to work.  Try "pip install beautifulsoup4".')
    sys.exit(1)

try:
    import requests
except ImportError:
    logging.critical('You must install "requests" for this script to work.  Try "pip install requests".')
    sys.exit(1)


def normalize_title(s):
    """
    Convert to lowercase and remove punctuation characters.
    """
    s = s.replace('&', 'and')
    s = s.replace('.', ' ')
    return ''.join(char for char in s.lower() if char not in string.punctuation)


def strings_match(s1, s2):
    """
    Return True if strings are at least 90% similar, False otherwise.

    Arguments s1 and s2 can each be either a single string or a list of possible matching strings.
    """

    if isinstance(s1, list):
        for item in s1:
            if strings_match(item, s2):
                return True
        return False

    if isinstance(s2, list):
        for item in s2:
            if strings_match(s1, item):
                return True
        return False

    matcher = SequenceMatcher(None, s1, s2)
    if matcher.ratio() >= 0.90:
        return True
    else:
        return False


def years_match(y1, y2):
    """
    Returns True if y1 and y2 are no more than 1 year apart, False otherwise.
    """
    for i in (-1, 0, 1):
        if y1 == str(int(y2) + i):
            return True
    return False


def check_predb(release_name):
    msg = 'Checking predb.me for "{release_name}"'
    logging.debug(msg.format(release_name=release_name))
    params = {
        'search': release_name,
        'cats': 'movies,-movies-discs',
    }
    try:
        response = requests.get('http://predb.me/', params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        matches = set(link.text.strip() for link in soup.find_all('a', class_='p-title'))
        return release_name in matches
    except Exception as e:
        logging.warning(e)
        return False
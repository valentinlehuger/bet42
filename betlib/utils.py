# -*- coding: utf-8 -*-
import unicodedata


ALIASES = {
    "u00c1": "A",
    "u00c2": "A",
    "u00c3": "A",
    "u00c4": "A",
    "u00c5": "A",
    "u00c6": "AE",
    u"u00e1": "a",
    u"u00e3": "a",
    u"u00e4": "a",
    u"u00e5": "a",
    u"u00e6": "ae",
    u"\xe7": "c",
    u"\xe9": "e",
    u"\xe8": "e",
    u"u00e9": "e",
    u"u00ea": "e",
    u"u00cd": "I",
    u"u00ed": "i",
    u"u00d1": "N",
    u"u00d3": "O",
    u"u00d4": "O",
    u"u00d5": "O",
    u"u00d6": "O",
    u"u00d8": "O",
    u"u00f3": "o",
    u"u00f4": "o",
    u"u00f5": "o",
    u"u00f6": "o",
    u"u00f7": "o",
    u"u00f8": "o",
    u"u00dc": "U",
    u"u00fa": "u",
    u"u00fb": "u",
    u"u00fc": "u"
}
#
# def normalize(name):
#
#     name = name.strip()
#     name = name.lower()
#     name = name.replace(u"\xe9", "e")
#     name = name.replace(u"\xe8", "e")
#     name = name.replace(u"\xe7", "c")
#     name = name.replace(u"-", " ")
#
#     return name





def normalize(data):
    """ Normalise (normalize) unicode data in Python to remove umlauts, accents etc. """

    # data = data.decode("utf-8")
    normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')

    for alias in ALIASES:
        normal = normal.replace(alias, ALIASES[alias])

    return normal


# if __name__ == "__main__":
#     str = "Valérïen
#     print normalize(str)

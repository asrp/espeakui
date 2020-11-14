# -*- coding: utf-8 -*-
languages = ["en"]
translate = {lang: list() for lang in languages}
data = """
∈, in
≤, less than or equal to
ε, epsilon
>, at least
<, at most
*, star
=, equal
⊆, subset of
. . ., dot dot dot
"""
for line in data.strip().split("\n"):
    line = line.split(",")
    source, targets = line[0], line[1:]
    for lang, target in zip(languages, targets):
        translate[lang].append((source.strip(), " %s " % target.strip()))

class regex:
    url = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    mdy = """(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+
                 [0-9]*(?:st|nd|rd|th)?,?\s* # Day
                 '?[0-9]*\s*                 # Year
                 |
                 [0-9]{2,4}[-/][0-9]{2}[-/][0-9]{2,4}
              )"""
    time = """(?:[0-9]*\:[0-9]*
                 (?:\s+(?:am|pm|AM|PM))?)"""
    timestamp = """%s\s+(?:\s*at\s*)?%s?""" % (mdy, time)

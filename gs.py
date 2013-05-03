#!/usr/bin/env python

import sys
import urllib
import urllib2

from HTMLParser import HTMLParser


useragent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36"

user = sys.argv[1]

bib_url = "http://scholar.google.com/citations?view_op=export_citations&hl=en&user=%s" % user
bib_params = "cit_fmt=0&export_selected_btn=Export+the+article+below&s=%s"

profile_url = "http://scholar.google.com/citations?user=%s&hl=en" % user


def get_bibtex(bib_id):
    bib_id = urllib.quote(bib_id)
    bib_req = urllib2.Request(bib_url, headers={'User-Agent' : useragent})
    bib_data = urllib2.urlopen(bib_req, bib_params % bib_id).read()

    return bib_data

# create a subclass and override the handler methods
class CitationParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if len(attr) >= 2 and attr[0] == "onclick" and \
               attr[1].startswith("return gs_ocit"):
                print attr[1][22:34]

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        pass

class ProfileParser(HTMLParser):
    citation_for_view = "citation_for_view="

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if len(attr) >= 2 and attr[0] == "href" and \
               attr[1].startswith("/citations?view_op=view_citation"):
                idx = attr[1].find(self.citation_for_view) + \
                    len(self.citation_for_view)
                bib_id = attr[1][idx:]
                print get_bibtex(bib_id)

# instantiate the parser and fed it some HTML
profile = ProfileParser()
req = urllib2.Request(profile_url, headers={'User-Agent' : useragent})
url_data = urllib2.urlopen(req).read()
profile.feed(url_data)

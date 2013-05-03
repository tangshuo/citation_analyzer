#!/usr/bin/env python

import sys
import urllib
import urllib2
import hashlib
import random
import glob

from HTMLParser import HTMLParser


useragent = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36"

user = sys.argv[1]

bib_url = "http://scholar.google.com/citations?view_op=export_citations&hl=en&user=%s" % user
bib_id_url = "http://scholar.google.com/scholar.bib?q=info:%s:scholar.google.com/&output=citation&hl=en"
bib_params = "cit_fmt=0&export_selected_btn=Export+the+article+below&s=%s"
google_id = hashlib.md5(str(random.random())).hexdigest()[:16]

def get_bibtex(bib_id):
    bib_id = urllib.quote(bib_id)
    bib_req = urllib2.Request(bib_url, headers={'User-Agent' : useragent})
    bib_data = urllib2.urlopen(bib_req, bib_params % bib_id).read()

    return bib_data

def get_bibtex_by_id(bib_id):
    bib_req = urllib2.Request(bib_id_url % bib_id, headers={'User-Agent' : useragent, 'Cookie' : 'GSP=ID=%s:CF=4' % google_id})
    bib_data = urllib2.urlopen(bib_req).read()

    return bib_data

def analyse(filename):
    bib_file = open(filename, 'r')
    print bib_file.read()
    bib_file.close()

class CitationSubPageParser(HTMLParser):
    bib_list = []

    def __init__(self, subpage):
        HTMLParser.__init__(self)
        self.bib_list = []
        req = urllib2.Request("http://scholar.google.com%s" % subpage, \
                              headers={'User-Agent' : useragent})
        url_data = urllib2.urlopen(req).read()
        self.feed(url_data)


    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if len(attr) >= 2 and attr[0] == "onclick" and \
               attr[1].startswith("return gs_ocit"):
                self.bib_list.append(attr[1][22:34])

    def get_bib_list(self):
        return self.bib_list

# create a subclass and override the handler methods
class CitationParser(HTMLParser):
    cite_url = "http://scholar.google.com/scholar?oi=bibs&hl=en&cites=%s&num=20"
    bib_list = []

    def __init__(self, cite_id):
        HTMLParser.__init__(self)
        self.bib_list = []
        req = urllib2.Request(self.cite_url % cite_id, \
                              headers={'User-Agent' : useragent})
        url_data = urllib2.urlopen(req).read()
        self.feed(url_data)

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if len(attr) >= 2 and attr[0] == "onclick" and \
               attr[1].startswith("return gs_ocit"):
                self.bib_list.append(attr[1][22:34])

        if len(attrs) == 2 and \
           len(attrs[0]) == 2 and attrs[0][0] == "class" and \
           attrs[0][1] == "gs_nma" and \
           len(attrs[1]) == 2 and attrs[1][0] == "href" and \
           attrs[1][1].encode('ascii','ignore').find("/scholar?start=") >= 0:
            subpage = CitationSubPageParser(attrs[1][1])
            self.bib_list.append(subpage.get_bib_list())

    def get_all_citations(self):
        return self.bib_list

class ProfileParser(HTMLParser):
    profile_url = "http://scholar.google.com/citations?user=%s&hl=en"
    citation_for_view = "citation_for_view="
    bib_file = None

    def __init__(self, profile_id):
        HTMLParser.__init__(self)
        self.bib_file = None
        req = urllib2.Request(self.profile_url % profile_id, \
                              headers={'User-Agent' : useragent})
        url_data = urllib2.urlopen(req).read()
        self.feed(url_data)
        self.calculate_citation()

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if len(attr) >= 2 and attr[0] == "href":
                if attr[1].startswith("/citations?view_op=view_citation"):
                    idx = attr[1].find(self.citation_for_view) + \
                          len(self.citation_for_view)
                    bib_id = attr[1][idx:]
                    self.calculate_citation()
                    self.bib_file = open("%s.bib" % bib_id.replace(':', '_'), 'w')
                    self.bib_file.write(get_bibtex(bib_id))
                elif attr[1].find("/scholar?oi=bibs&hl=en&") > 0:
                    idx = attr[1].find("cites=") + len("cites=")
                    cite_id = attr[1][idx:]
                    c_parser = CitationParser(cite_id)
                    for citation in  c_parser.get_all_citations():
                        self.bib_file.write(get_bibtex_by_id(citation))

    def calculate_citation(self):
        if self.bib_file is not None:
            filename = self.bib_file.name
            self.bib_file.close()
            analyse(filename)

# instantiate the parser and fed it some HTML
#ProfileParser(user)
for filename in glob.glob("*.bib"):
    analyse(filename)

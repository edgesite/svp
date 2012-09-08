import os
import sys
from xml.xslt.Processor import Processor
# import cgi

# parse query string and instantiate xslt proc
# query = cgi.FieldStorage()

def convert_spread():
    xsltproc = Processor()
    xsltproc.appendStylsheetUri("templ.xsl")
    html = xsltproc.runUri("temp.xml")

def main():
    convert_spread()

if __name__ == "__main__":
    main()


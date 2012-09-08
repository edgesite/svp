'''
 A module for getting information about Lotus 1-2-3 files.
 The inputs are a filepath and an outpath.
'''

import os

def make_html(inpath, outpath):
    os.popen2("ssconvert --import-encoding=Gnumeric_lotus:lotus --export-type=Gnumeric_html:html40 " + inpath + " " + outpath)

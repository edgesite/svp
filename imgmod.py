'''
 This module will convert various types of images to (in our project) .jpg 
'''

import os, sys
import PIL.Image

def make_jpg(inpath, outpath):
    try:
        im = PIL.Image.open(inpath)
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.save(outpath)
    except IOError:
        sys.stderr.write("\n\nCannot convert " + inpath + "\n\n")

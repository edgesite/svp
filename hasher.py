import md5 
import os
import sys

'''
 md5sum(filepath, list of conversions)
 returns the md5 hash of the given file path with an extension.
 the extension is determined by the conversion list sent to the
 function; the original file's extension is looked up in the
 conversion list.
'''
def md5sum(fpath, convlist):
    m = md5.new()
    try:
        m.update(fpath)
    except IOError, msg:
        return '0', msg
    extnsn = fpath.split('.')[-1]

    for ls in convlist:
        for ext in ls:
            if extnsn.lower() != ls[-2] and extnsn.lower() == ext:
            #if ext != ls[-1] and extnsn == ext:
                return m.hexdigest() + '.' + ls[-2]
                #return '-1'
    return '-1'

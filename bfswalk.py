'''
'''

import os, sys
import stat

# Do a full walk of the directory, default breadth first
def walktree (top = ".", depthfirst = False):
    names = os.listdir(top)
    if not depthfirst:
        yield top, names
    for name in names:
        try:
            st = os.lstat(os.path.join(top, name))
        except os.error:
            continue
        if stat.S_ISDIR(st.st_mode):
            for (newtop, children) in walktree (os.path.join(top, name), depthfirst):
                yield newtop, children
    if depthfirst:
        yield top, names

# dname must be at the appropriate level for the mount to have kicked
# in - i.e. /mnt/isosrv/image_30000038608679/30000038608679/ (passed in
# as sys.argv[1] here, but read from a string in our real code)
def gencnames(dname):
    flist = []
    for (basepath, children) in walktree(dname, False):
        for child in children:
            #sys.stderr.write(os.path.join(basepath, child))
            if not os.path.isdir(os.path.join(basepath, child)):
                flist.append(os.path.join(basepath, child))
    return flist

if __name__ == '__main__':
    gencnames(sys.argv[1])



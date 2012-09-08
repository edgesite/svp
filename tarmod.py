'''
 This module is designed for browsing through tar archives
 and examining the files within without the bother of
 extraction.  It will display the contents of the archives
 via the same template as is used with the regular directories.
'''
#django utilities

from django.http import HttpResponse
from django.template import loader, Template, Context, TemplateDoesNotExist

#modules from our project

import mimefinder, static

#system modules

import mimetypes, os, tarfile

def examinetar(request, tarpath, fpath=None, document_root=None, show_indexes=False):

    if fpath:
        # Got a valid fpath (inside the tarfile)
        tarpath = document_root + tarpath + "/" + fpath
    else:
        # No valid fpath (tarfile itself)
        tarpath = document_root + tarpath

    if fpath == None:
        try:
            t = loader.get_template('/u/savagev/valtest/realtest/templates/data/static/directory_index.html')
        except TemplateDoesNotExist:
            t = loader.get_template('/u/kamwoods/Sudoc/svp/realtest/templates/data/static/directory_index.html')

        tar = tarfile.open(tarpath, 'r')
    
        files = []
        for tarinfo in tar:
            f = tarpath.split('/')[-1] +'/'+ tarinfo.name
            filefp = os.path.join(tarpath, f)
            mimetype = mimefinder.find_type(filefp)
            fmodtime = tarinfo.mtime
            if not tarinfo.isdir():
                fgsize = static.greek(tarinfo.size)
            else:
                fgsize = "-"

            files.append(["-",
                          "",
                          mimetype,
                          f,
                          fmodtime,
                          fgsize,])

        tar.close()
    
        c = Context({
            'directory' : tarpath+'/',
            'file_list' : files,
            'hinst': request.session['hinst'],
            'hexe': request.session['hexe'],
            'hdriver': request.session['hdriver'],
            'hlib': request.session['hlib'],
            'hetc': request.session['hetc'],
            'user': request.user.username,
        }) 

        return HttpResponse(t.render(c))

    else:
        # Inside the tarfile (set up the appropriate path)
        tarmainpath = "/".join([x for x in tarpath.split("/")[0:-1]])

        tar = tarfile.open(tarmainpath, 'r')
        tarredfile = tarpath.split('/')[-1]
        extractpath = '/tmp/' + tarredfile

        thefile = tar.extract(tarredfile, "/tmp")
        content = open(extractpath, 'rb').read()

        mimetype = mimetypes.guess_type(extractpath)[0]
        return HttpResponse(content, mimetype=mimetype)

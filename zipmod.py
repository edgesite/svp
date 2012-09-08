'''
 This module is designed for browsing through zip archives
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

import mimetypes, os, zipfile

def examinezip(request, tarpath, fpath=None, document_root=None, show_indexes=False):

    if fpath:
        # Got a valid fpath (inside the zipfile)
        zippath = document_root + zippath + "/" + fpath
    else:
        # No valid fpath (zipfile itself)
        zippath = document_root + zippath

    if fpath == None:
        try:
            t = loader.get_template('/u/savagev/valtest/realtest/templates/data/static/directory_index.html')
        except TemplateDoesNotExist:
            t = loader.get_template('/u/kamwoods/Sudoc/svp/realtest/templates/data/static/directory_index.html')

        zip = zipfile.open(tarpath, 'r')

        files = []
        for zipinfo in zip:
            f = zippath.split('/')[-1] +'/'+ zipinfo.filename
            filefp = os.path.join(zippath, f)
            mimetype = mimefinder.find_type(filefp)
            fmodtime = zipinfo.date_time
            if not tarinfo.file_size == 0:
                fgsize = static.greek(zipinfo.file_size)
            else:
                fgsize = "-"

            files.append(["-",
                          "",
                          mimetype,
                          f,
                          fmodtime,
                          fgsize,])

        zip.close()

        c = Context({
            'directory' : zippath+'/',
            'file_list' : files,
            'hinst': request.session['hinst'],
            'hexe': request.session['hexe'],
            'hdriver': request.session['hdriver'],
            'hlib': request.session['hlib'],
            'hetc': request.session['hetc'],
            'user': request.user.username,
        })

        return HttpResponse(t.render(c))

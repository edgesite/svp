#django utilities

from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.template import loader, Template, Context, TemplateDoesNotExist

#our django models

from realtest.data.models import MaskFile, Conversion

#modules from our project

import bfswalk, dbfmod, hasher, imgmod, lotusmod, mdbmod, mimefinder, runconvert, tarmod, xlsmod, flvconvert

#system modules

import mimetypes, operator, os, posixpath, re, rfc822, shutil, stat, string, sys, time, urllib

_abbrevs = [
    (1<<50L, 'P'),
    (1<<40L, 'T'), 
    (1<<30L, 'G'), 
    (1<<20L, 'M'), 
    (1<<10L, 'k'),
    (1, 'b')
    ]

def greek(size):
    """Return a string representing the greek/metric suffix of a size"""
    for factor, suffix in _abbrevs:
        if size > factor:
            break
    return `int(size/factor)` + suffix

def ungreek(size):
    if size == '-':
        return '-'
    """Return a string representing the greek/metric suffix of a size"""
    for factor, suffix in _abbrevs:
        if size[-1] == suffix:
            return int(size[:-1])*factor

_monthdict = [
    ('Jan', '01'), ('Feb', '02'), ('Mar', '03'),
    ('Apr', '04'), ('May', '05'), ('Jun', '06'),
    ('Jul', '07'), ('Aug', '08'), ('Sep', '09'),
    ('Oct', '10'), ('Nov', '11'), ('Dec', '12')  ]

def conv_date(date):
    # This accepts the date in (Python standard) dayofweek month dd hh:mm:ss yyyy form 
    # and changes it to (Apache standard) dd-month-yyyy hh:mm form
    # Split apart the pieces of the date
    #if the dd is a single digit, there will be an empty piece
    if date.split(" ")[2] == '':
        dayofweek, month, emptyspace, dd, time, yyyy = date.split(" ")
    else:
        dayofweek, month, dd, time, yyyy = date.split(" ")
    #split apart the time
    hh, mm, ss = time.split(":")
    #rebuild it
    datestr = ""
    if int(dd) < 10:
        datestr += "0"
    datestr += dd + "-" + month + "-" + yyyy + " " + hh + ":" + mm
    return datestr

def std_date(date):
    # This accepts the date in (Apache standard) dd-month-yyyy hh:mm form and changes 
    # it to (comparable) yyyymmddhhmm form
    #break it into date and time
    date, time = str(date).split(" ")
    #break up the time
    hh, mm = time.split(":")
    #break up the date
    dd, month, yyyy = date.split("-")
    mm = '00'
    #set the month to numeric month instead of alphabetic
    for strmonth, nummonth in _monthdict:
        if month == strmonth:
            mm = nummonth
            break
    #make it a full string
    thedate = yyyy + mm + dd + hh + mm
    #turn it into an integer
    thedate = int(thedate)
    return thedate

def sort_by_index(sequence, ind):
    if ind == 4:
        decorated = [(std_date(x[4]), x) for x in sequence]
    elif ind == 5:
        decorated = [(ungreek(x[5]), x) for x in sequence]
    else:
        decorated = [(x[ind], x) for x in sequence]
    decorated.sort()
    return [x[1] for x in decorated]

def serve(request, path, document_root=None, show_indexes=False):
    """
    Serve static files below a given point in the directory structure.
    To use, put a URL pattern such as::
        (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root' : '/path/to/my/files/'})
    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  
    """

    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    newpath = ''
    for part in path.split('/'):
        if not part:
            # strip empty path components
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # strip '.' and '..' in path
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = os.path.join(document_root, newpath)
    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(newpath, fullpath,
                                   request.session['hinst'],
                                   request.session['hexe'],
                                   request.session['hlib'], 
                                   request.session['hetc'], 
                                   request.session['hdriver'],
                                   request.META['REMOTE_ADDR'],
                                   request.META['QUERY_STRING'],
                                   request.user)
        raise Http404, "Directory indexes are not allowed here."
    if not os.path.exists(fullpath):
        raise Http404, '"%s" does not exist' % fullpath
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified()

    # Convert any file that is an md5sum and has not already been converted.
    # We want to do this only for those files that are not converted by the
    # daemon or are not IN THE PROCESS OF being converted
    # DO THIS LATER, IT'S THE CORRECT PLACE
 
    mimetype = mimetypes.guess_type(fullpath)[0]
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = rfc822.formatdate(statobj[stat.ST_MTIME])
    return response

def directory_index(path, fullpath, hinst, hexe, hlib, hetc, hdriver, ip, sorter, user):

    """
    This function is the veritable life-blood of the project.
    Silently, it sneaks through the directory structure, furtively collecting names of files
    (as well as their most personal information, like size and last date accessed).  If the
    files are among the chosen with special marks upon their paths (.gif, .doc, .xls, and
    the like), it thrusts them upon various converting modules to change their very being
    and display the copies alongside the originals.  Can you tell the difference?
    And it doesn't stop there.  If asked, this function can reorder its finds based on various
    qualifications, or even hide them from the user by relegating them to a separate list from
    the regular files.
    
    """

    try:
        t = loader.get_template('/u/savagev/valtest/realtest/templates/data/static/directory_index.html')
    except TemplateDoesNotExist:
        t = loader.get_template('/u/kamwoods/Sudoc/svp/realtest/templates/data/static/directory_index.html')

    files = []
    mfiles = []
    x = []

    convs = []
    vidconvs = []
    # Fix this - it only needs to happen once
    for clist in Conversion.objects.filter():
        lst = clist.fromlist.split(', ')
        lst.append(clist.toextension)
        lst.append(clist.async)

        if clist.toextension == 'flv':
            vidconvs.append(lst)
        convs.append(lst)

    # Set up the stuff for runconvert
    curdir = fullpath.split("/")[-1]
    brcd = (fullpath.split("/")[3]).split("_")[1]
    # only call this function if the user is browsing the top-level directory
    if len(curdir) > 6 and brcd == curdir[6:]:
        # Will fork off and do appropriate work
        runconvert.runconv(fullpath, convs)
        flvconvert.runconv(fullpath, vidconvs)
        #this needs to think about FLVRUNCONVERT somehow
        #pass

    # Test to see if output directory exists. Only create if it does not
    # (i.e. on first pass into the directory)
    if os.path.isdir("/tmp/migrated/" + brcd):
        pass
    elif os.path.isfile("/tmp/migrated/" + brcd):
        raise OSError("a file with that name already exists")
    else:
        os.mkdir("/tmp/migrated/" + brcd)

    for f in os.listdir(fullpath):
        if not f.startswith('.'):
            filefp = os.path.join(fullpath, f)
            mimetype = mimefinder.find_type(filefp)
            migrated = hasher.md5sum(filefp, convs)
            #this is for the actual conversions that happen at the bottom
            mig = migrated
            migratedext = ""
            if not migrated == '-':
                try:
                    migratedext = "/data/static/" + migrated.split('.')[-1] + ".gif"
                except:
                    migratedext = "/data/static/unknown.gif"
            fmodtime = conv_date(time.asctime(time.localtime(os.stat(filefp).st_mtime)))
            if not os.path.isdir(filefp):
                fgsize = greek(os.stat(filefp).st_size)
            else:
                fgsize = "-"
            
            '''
            The logic of this loop needs to be fixed.  It is intended to
            determine whether there are masked files in the directory and
            accordingly put them into the mfiles (masked files) list if necessary.
            However, Kam wanted to get rid of the extraneous appendings to the two
            file lists.  Right now... not so much.
            '''

            try:
                i = MaskFile.objects.filter(full_path__exact=filefp)[0]
                if (hinst and i.mask_flag) and not i.restrict_flag:
                    if os.path.isdir(filefp):
                        mfiles.append([filefp,
                                       fmodtime,
                                       fgsize])
                    else:
                        mfiles.append([i.file_name,
                                       fmodtime,
                                       fgsize])
                else:
                    if len(migrated) > 2:
                        migrated = "/tmp/migrated/" + brcd + "/" + migrated
                    else:
                        migrated = "-"

                    files.append([migrated,
                                  migratedext,
                                  mimetype,
                                  f,
                                  fmodtime,
                                  fgsize,
                                  ])
            except:
                #this should be fixed sometime (-1 test, hahah)
                if len(migrated) > 2:
                    migrated = "/tmp/migrated/" + brcd + "/" + migrated
                else:
                    migrated = '-'
                if (hexe and mimetype=="binary.gif") or (hlib and mimetype=="binary.gif"):
                    mfiles.append([f,
                                   fmodtime,
                                   fgsize])
                else:
                    files.append([migrated,
                                  migratedext,
                                  mimetype,
                                  f,
                                  fmodtime,
                                  fgsize,
                                  ])
 

            # Don't forget to check for whether we SHOULD be migrating these files
            # on the fly
            for l in convs:
                if filefp[-3:].lower() in l:
                    if l[-1] == False:
                        if not os.path.isfile(migrated):
                            if not migrated == '-':

                                 # First test for dbf files
                                 if filefp[-3:].lower() == "dbf":
                                     out_fp = open('/tmp/migrated/'+brcd+'/'+mig, 'w')
                                     dbfmod.make_list_lim(dbfmod.DBFFile(filefp), out=out_fp)
                                     out_fp.close()
 
                                 elif filefp[-3:].lower() == "cdf":
                                     #uses skeletontable utility.  Kam says it's a hack
                                     #os.popen2('/u/savagev/cdf31-dist/bin/skeletontable -skeleton /tmp/migrated/' + brcd + '/' + mig[:-4] + ' ' + filefp)
                                     os.popen2('/u/kamwoods/cdf31-dist/bin/skeletontable -skeleton /tmp/migrated/' + brcd + '/' + mig[:-4] + ' ' + filefp)

                                 elif filefp[-3:].lower() == "xls":
                                     #uses xlrd to convert it
                                     xlsmod.make_html(filefp, migrated)

                                 elif filefp[-3:].lower() == "mdb":
                                     mdbmod.make_html(filefp, migrated)

                                 elif filefp[-3:-1].lower() == 'wk' or filefp[-3:] == '123':
                                     lotusmod.make_html(filefp, migrated)

                                 else:             
                                 # Otherwise this is an image conversion
                                     imgmod.make_jpg(filefp, '/tmp/migrated/'+brcd+'/'+mig)
                                     #os.popen2('convert ' + filefp + ' /tmp/migrated/'+brcd+'/'+mig)

                                 # Add remaining conversions later
                                 # Don't forget excel (python xlrd - google it) - copy into p2.4 site-packages

    name = mod = size = 'a'
    # Ignore if no default sort has been passed in - THIS IS CRUFTY
    if not sorter == '':
        #parse out the bit of the query string that details what the objects are to be sorted by
        pieces = sorter.split(";")
        sorter = pieces[0].split("=")[-1]
        order = pieces[1].split("=")[-1]
        # sort by size
        if sorter == 's':
            sortind = 5 
            if order == 'a':
                size = 'd'
        # sort by mod-time
        elif sorter == 'm':
            sortind = 4
            if order == 'a':
                mod = 'd'
        # sort by name
        else:
            sortind = 3
            if order == 'a':
                name = 'd'
        sys.stderr.write(str(files[1][4]))
        files = sort_by_index(files, sortind)
        if order == 'd':
            files.reverse()

    c = Context({
        'brcd': brcd,
        'directory' : path + '/',
        'file_list' : files,
        'hinst': hinst,
        'hexe': hexe,
        'hdriver': hdriver,
        'hlib': hlib,
        'hetc': hetc,
        'ip': ip,
        'mask_file_list': mfiles,
        'mod': mod,
        'name': name,
        'size': size,
        'user': user.username,
    })
    return HttpResponse(t.render(c))

def was_modified_since(header=None, mtime=0, size=0):
    """
    Was something modified since the user last downloaded it?

    header
      This is the value of the If-Modified-Since header.  If this is None,
      I'll just return True.

    mtime
      This is the modification time of the item we're talking about.

    size
      This is the size of the item we're talking about.
    """
    try:
        if header is None:
            raise ValueError
        matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header,
                           re.IGNORECASE)
        header_mtime = rfc822.mktime_tz(rfc822.parsedate_tz(
            matches.group(1)))
        header_len = matches.group(3)
        if header_len and int(header_len) != size:
            raise ValueError
        if mtime > header_mtime:
            raise ValueError
    except (AttributeError, ValueError):
        return True
    return False

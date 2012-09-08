"""
 Functions that call pages:
   contacts(request) - contacts page
   edits(request, Barcode_No) - past metadata added to an entry
   index(request) - the main page
   match(request, Barcode_No) - in-depth information about an entry
   preferences(request) - change masking flags
   results(request) - entries that match the user's search
   saved(request) - saves the mask flag changes from preferences

 Functions that do not currently do anything:
   show(request) - display the directory structure
   upload(request) - user uploads a file to the database
"""

#django utilities

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

#our own models

from realtest.data.models import Iso, AddedFile, MetaMod, Biblio, AllowByIP

#system modules

from datetime import datetime
import os, sys

'''
 takes only a request as its argument
 queries the svn repository and updates the recent changes page
'''

def changes(request):
    shd = os.popen2("svn log file:///u/svp/Projects/svp/trunk")
    lines = shd[1].readlines()
    shd[1].close()
    shd[0].close()
    return render_to_response('data/changes.html',
                             {'changes': lines[:53],
                              'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                              'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                              'hdriver': request.session['hdriver'],
                              'ip': request.META['REMOTE_ADDR'],
                              'user': request.user, })

'''
 takes only a request as its argument
 opens the contacts page
'''
def contacts(request):
    return render_to_response('data/contacts.html',
                             {'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                              'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                              'hdriver': request.session['hdriver'],
                              'ip': request.META['REMOTE_ADDR'],
                              'user': request.user, })

'''
 takes a request and a barcode number (given by a form) as its arguments
 checks the database to see if the barcode number has any metadata edits
 associated with it.
'''
def edits(request, Barcode_No):
    datum = MetaMod.objects.filter(iso_num__exact=Barcode_No)
    avail = "Sorry, there are no previous edits to display."
    try:
    #Try to see if there is actually data
        avail = datum[0].username
        avail = "Previous edits for barcode " + Barcode_No
    except:
        pass
    #we need to script this so that the user can choose how many edits s/he would like to see
    try:
        return render_to_response('data/edits.html',
                                 {'avail': avail,
                                  'brcd': Barcode_No,
                                  'datum': datum[-5:], 
                                  'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                                  'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                                  'hdriver': request.session['hdriver'],
                                  'ip': request.META['REMOTE_ADDR'],
                                  'user': request.user, })
    except:
        return render_to_response('data/edits.html',
                                 {'avail': avail,
                                  'brcd': Barcode_No,
                                  'datum': datum, 
                                  'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                                  'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                                  'hdriver': request.session['hdriver'],
                                  'ip': request.META['REMOTE_ADDR'],
                                  'user': request.user, })

'''
 takes only a request as its argument
 checks to see if there are cookies set in the user's session for the
 various masking flags, and, if no cookies are yet set, sets them to false
'''
def index(request):
    try:
        request.session['hinst'] = request.session['hinst']
    except:
        request.session['hinst'] = False
    try:
        request.session['hexe'] = request.session['hexe']
    except:
        request.session['hexe'] = False
    try:
        request.session['hlib'] = request.session['hlib']
    except:
        request.session['hlib'] = False
    try:
        request.session['hetc'] = request.session['hetc']
    except:
        request.session['hetc'] = False
    try:
        request.session['hdriver'] = request.session['hdriver']
    except:
        request.session['hdriver'] = False
    return render_to_response('data/index.html',
                             {'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                              'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                              'hdriver': request.session['hdriver'],
                              'ip': request.META['REMOTE_ADDR'],
                              'user': request.user, })

'''
 takes a request and a barcode number (given by a form) as its arguments
 displays the library's catalog card for the barcode number's corresponding
 catalog key.  also displays any metadata that users may have added and gives
 an opportunity to add more based on permissions
'''
def match(request, Barcode_No):
    success = ""
    #sys.stderr.write(str(request.user.get_group_permissions())+"\n")
    somethingelse = ""
    #manipulator = MetaMod.AddManipulator()
    #pdata = request.POST.copy()
    try:
        dmm = MetaMod(new_data=request.POST['metadata'], date_stamp=datetime.now(), username=request.user.username, iso_num=Barcode_No)
        if request.user.has_perm('data.add_metamod'):
            dmm.save()
            success = "Metadata updated successfully."
        else:
            success = "Sorry, you don't have permissions to add that."
    except:
        pass
    iso = get_object_or_404(Iso, pk=Barcode_No)
    ttl = iso.Title.split('|')
    iso.Title = ""
    for piece in ttl:
        if not piece == ttl[0]:
            iso.Title = iso.Title + '<br>' + piece[1:]
        else:
            iso.Title += piece
    request.session['mp'] = "/mnt/isosrv/image_"+str(Barcode_No)+"/"+str(Barcode_No)
    try:
        disppage = Biblio.objects.filter(Catalog_Key__exact=iso.Catalog_Key)[0].Bib_Entry
    except:
        disppage = False
    return render_to_response('data/match.html', 
                             {'additional': MetaMod.objects.filter(iso_num__exact=Barcode_No),
                              'disppage': disppage,
                              'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                              'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                              'hdriver': request.session['hdriver'],
                              'ip': request.META['REMOTE_ADDR'],
                              'iso': iso,
                              'success': success,
                              'user': request.user, })

'''
 takes only a request as its argument
 simple call to a page where the user can change his/her preferences
'''
#@login_required
def preferences(request):
    return render_to_response('data/preferences.html',
                             {'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                              'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                              'hdriver': request.session['hdriver'],
                              'ip': request.META['REMOTE_ADDR'],
                              'user': request.user, })
preferences = login_required(preferences)

'''
 takes only a request as its argument
 checks the database for any isos whose titles contain the post data
 filters the isos based on whether the user's IP address is permitted to see them
'''
def results(request):
    searchstr = request.POST['srch']
    i = Iso.objects.filter(Title__icontains=searchstr)
    # Have to do something like this because ISO_created date is not null by default
    j = i.filter(Q(ISO_created__contains="19") | Q(ISO_created__contains="20"))
    # Pulling out the pipes in the title
    ttl = []
    for iso in j:
        ttl = iso.Title.split('|')
        iso.Title = ""
        for piece in ttl:
            if not piece == ttl[0]:
                iso.Title = iso.Title + '<br>' + piece[1:]
            else:
                iso.Title += piece

    #this checks through the AllowByIP entries and determines whether the user is allowed to see each
    restricted = 0
    newj = []
    for iso in j:
        try:
            abip = AllowByIP.objects.filter(Barcode__exact=iso.Barcode_No)[0]
            isok = False
            for subnet in abip.Allow_Subnets:
                if subnet == request.META['REMOTE_ADDR'].split('.')[2]:
                    isok = True
            #if the user is not allowed to see the iso, add 1 to the number of restricted isos and
            #remove the iso from the list
            if isok:
                newj.append(iso)
            else:
                restricted += 1
        except:
            newj.append(iso)
            pass  
    
    c = j.count() - restricted
    return render_to_response('data/results.html', 
                             {'count': c,
                              'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                              'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                              'hdriver': request.session['hdriver'],
                              'ip': request.META['REMOTE_ADDR'],
                              'isos': newj,
                              'posted': request.POST['srch'],
                              'restricted': restricted,
                              'user': request.user, })

'''
 takes only a request as its argument
 receives the data posted by the preferences page and stores the information
 in the appropriate variables
'''
def saved(request):
    request.session['restrict'] = True
    try:
         request.session['hexe'] = request.POST['hexe']
         request.session['hexe'] = True
    except:
         request.session['hexe'] = False
    try:
         request.session['hinst'] = request.POST['hinst']
         request.session['hinst'] = True
    except:
         request.session['hinst'] = False
    try:
         request.session['hetc'] = request.POST['hetc']
         request.session['hetc'] = True
    except:
         request.session['hetc'] = False
    try:
         request.session['hlib'] = request.POST['hlib']
         request.session['hlib'] = True
    except:
         request.session['hlib'] = False
    try:
         request.session['hdriver'] = request.POST['hdriver']
         request.session['hdriver'] = True
    except:
         request.session['hdriver'] = False
    return render_to_response('data/saved.html', 
                             {'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
                              'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
                              'hdriver': request.session['hdriver'],
                              'ip': request.META['REMOTE_ADDR'],
                              'user': request.user, })

'''
 takes a request
'''
def view_video(request, path):
    return render_to_response('data/video.html',
                             {'video': path, })

'''
 THIS FUNCTION DOES NOT WORK
 show was originally our own write of static.serve
 all things we intended to handle with show are now handled in static.py by the serve
 and directory_index functions
'''
def show(request, Barcode_No):
    pass

'''
 THIS FUNCTION DOES NOT WORK
 takes only a request as its argument
 intended to allow users to upload their own files to the database and associate
 them properly with a given barcode
'''
#def upload(request):
#    addedfiles = new AddedFile(uploader="NONE", file=newdata['thefile'], csv_isolist=['00000'])
#    try:
#        new_data=request.POST.copy()
#        new_data.update(request.FILES)
#        manipulator=addedfiles.AddManipulator()
#        manipulator.do_html2python(new_data)
#        errors = manipulator.get_validation_errors(new_data)
#        if not errors:
#            AddedFile = manipulator.save(new_data)
#        return render_to_response('data/upload.html', {
#                                  'hinst': request.session['hinst'], 'hetc': request.session['hetc'], 
#                                  'hexe': request.session['hexe'], 'hlib': request.session['hlib'], 
#                                  'hdriver': request.session['hdriver'], 
#                                  'ip': request.META['REMOTE_ADDR'],
#                                  'user': request.user, })
#    except:
#        Manipulator=addedfiles.AddManipulator()
#        Form=formfields.FormWrapper(Manipulator,{},{})
#        Template=template_loader.get_template('data/upload.html')
#        Context=DjangoContext(request, {
#                             'form':Form,
#                             'hinst': request.session['hinst'], 'hetc': request.session['hetc'],
#                             'hexe': request.session['hexe'], 'hlib': request.session['hlib'],
#                             'hdriver': request.session['hdriver'],
#                            'ip': request.META['REMOTE_ADDR'],
#                             'success': "File added successfully.",
#                             'user': request.user, })
#        return HttpResponse(Template.render(Context))

# ----------------- 

#    if request.POST:
#        new_data = request.POST.copy()
#        new_data.update(request.FILES)
#    try:
        #f = AddedFile(uploader="NONE", file="tmpstr", csv_isolist=request.POST['isolist'])
#        f = AddedFile(uploader="NONE", file=newdata['thefile'], csv_isolist=newdata['isolist'])
#        f.save()
#        sys.stderr.write("Created " + str(f.file) + '\n')
#        sys.stderr.write("Created " + str(f.csv_isolist) + '\n')
#    except:
#        sys.stderr.write("Didn't create or save file object." + '\n') 
#    return render_to_response('data/upload.html', 
#                             {'hinst': request.session['hinst'], 'hetc': request.session['hetc'], 
#                              'hexe': request.session['hexe'], 'hlib': request.session['hlib'], 
#                              'hdriver': request.session['hdriver'], 
#                              'ip': request.META['REMOTE_ADDR'],
#                              'user': request.user, })

import mimetypes, os

'''
 find_type(objpath)
 takes an object's path and does a dictionary lookup of the extension.
 the outputs of the dictionary lookups are links to images corresponding
 to various file types/extensions
'''

def find_type(objpath):
    mimetype = ""
    try:
        ext = objpath.split('.')[-1].lower()
        extdic = { 'wrd': 'doc.gif', 'doc': 'doc.gif', 
                   'pdf': 'pdf.gif',
                   'cdf': 'cdf.gif', 
                   'html': 'html.gif', 'htm': 'html.gif', 
                   'gif': 'image.gif', 'jpg': 'image.gif', 'jpeg': 'image.gif', 
                   'tiff': 'image.gif', 'tif': 'image.gif', 'bmp': 'image.gif',
                   'pcx': 'image.gif',
                   'wav': 'sound.gif', 'mp3': 'sound.gif', 'ra': 'sound.gif',
                   'avi': 'video.gif', 'mpg': 'video.gif', 'mpeg': 'video.gif',
                   'mov': 'quicktime.gif',
                   'exe': 'binary.gif', 'bin': 'binary.gif',
                   'dll': 'dll.gif',
                   'tar': 'tar.gif',
                   'gz': 'gzip.gif',
                   'zip': 'zip.gif',
                   'txt': 'text.gif',
                   'ppt': 'ppt.gif', 
                   'xls': 'xls.gif', 'dbf': 'dbf.gif' }
        mimetype = extdic[ext]
    except:
        try:
            typestr = mimetypes.guess_type(objpath)[0]
            type = typestr.split('/')[0]
            typedic = { 'application': 'binary.gif',
                       'audio': 'sound.gif',
                       'image': 'image.gif',
                       'text': 'txt.gif',
                       'video': 'video.gif',}
            mimetype = typedic[type]
        except:
            if os.path.isdir(objpath):
                mimetype = 'folder.gif'
            else:
                mimetype = 'unknown.gif'
    return mimetype

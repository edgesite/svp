'''
 This module will convert videos from mpg to flv
'''

import commands, os, sys

def make_flv(inpath, outpath):
    #if inpath is None:
    #    return "No video selected"
    #filename = outpath
    #print "Konvertiere Quelldatei: %s" + filename
    #if filename is None:
    #    return "Video mit unbekanntem Dateinamen"
    #sourcefile = inpath
    #flvfilename = outpath
    #thumbnailfilename = "%svideos/flv/%s.png" % (settings.MEDIA_ROOT, video.id)
    #targetfile = outpath

    brcd = '30000078832189'

    #/tmp/migrated/ brcd
    if os.path.isdir("/tmp/migrated/" + brcd):
        pass
    elif os.path.isfile("/tmp/migrated/" + brcd):
        raise OSError("a file with that name already exists")
    else:
        os.mkdir("/tmp/migrated/" + brcd)

    ffmpeg = "ffmpeg -i %s -acodec mp3 -ar 22050 -ab 32 -f flv -s 320x240 %s" % (inpath,  outpath)
    #grabimage = "ffmpeg -y -i %s -vframes 1 -ss 00:00:02 -an -vcodec png -f rawvideo -s 320x240 %s " % (sourcefile, thumbnailfilename)
    flvtool = "flvtool2 -U %s" % outpath
    print ("Source : %s" % inpath)
    print ("Target : %s" % outpath)
    print ("FFMPEG: %s" % ffmpeg)
    print ("FLVTOOL: %s" % flvtool)
    try:
        ffmpegresult = "none"
        #os.popen2(ffmpeg)
        ffmpegresult = commands.getoutput(ffmpeg)
        print "-------------------- FFMPEG ------------------"
        print ffmpegresult
        # Check if file exists and is > 0 Bytes
        try:
            s = os.stat(targetfile)
            print s
            fsize = s.st_size
            if (fsize == 0):
                print "File is 0 Bytes. gross!"
                os.remove(targetfile)
                return ffmpegresult
            print "Germanically challenged file size is %i" % fsize
        except:
            print sys.exc_info()
            print "German-ness says that %s = the Holocaust.  It doesn't exist!" % outpath
            return ffmpegresult
        flvresult = "none"
        #os.popen2(flvtool)
        flvresult = commands.getoutput(flvtool)
        print "-------------------- FLVTOOL ------------------"
        print flvresult
     #   grab = commands.getoutput(grabimage)
      #  print "-------------------- GRAB IMAGE ------------------"
       # print grab
    except:
        print sys.exc_info()
    #    return sys.exc_info[1]
    return None

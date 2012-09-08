import commands, signal, os, sys, time, fcntl, select, bfswalk, hasher

def runchild(stdin, stdout, stderr, convlst, pid):

    si = file(stdin, 'r')
    #so = stdout
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
   
    for i in range(len(convlst)):
        inpath = convlst[i]
        outpath = convlst[i+len(convlst)/2]+'.flv'

 
        ffmpeg = "ffmpeg -i %s -acodec mp3 -ar 22050 -ab 32 -f flv -s 320x240 %s" % (inpath,  outpath)
        flvtool = "flvtool2 -U %s" % outpath
        try:
            ffmpegresult = "none"
            #ffmpegresult = commands.getoutput(ffmpeg)
            fin, fout = os.popen2(ffmpeg)
            for l in fout:
                so.write(l)
            # Check if file exists and is > 0 Bytes
            #try:
            #    s = os.stat(targetfile)
            #    fsize = s.st_size
            #    if (fsize == 0):
            #        os.remove(targetfile)
            #        continue
            #except:
            #    sys.stderr.write("failed on targetresult")
            #flvresult = "none"
            #flvresult = commands.getoutput(flvtool)
        except:
            sys.stderr.write("failed on convert -- %s" % outpath[14:]) 

    so.write("done")
    so.close()
    se.close()
    return 1

def genlist(fullpath, convs):
    flst = []
    mlst = []
    curdir = fullpath.split("/")[-1]

    brcd = (fullpath.split("/")[3]).split("_")[1]

    mconv = []
    for l in convs:
        if l[-1]:
            mconv.append(l)

    for f in os.listdir(fullpath):

        if not f.startswith('.'):
            for i in bfswalk.gencnames(os.path.join(fullpath, f)):
                m = hasher.md5sum(i, mconv)

                if not m == '-1':
                    flst.append(i)
                    mlst.append("/tmp/migrated/" + brcd + "/" + m[:-4])

    flst += mlst
    if os.path.isdir("/tmp/migrated/" + brcd):
        pass
    elif os.path.isfile("/tmp/migrated/" + brcd):
        raise OSError("a file with that name already exists")
    else:
        os.mkdir("/tmp/migrated/" + brcd)
    
    if os.path.isdir("/tmp/video/" + brcd):
        pass
    elif os.path.isfile("/tmp/video/" + brcd):
        raise OSError("a file with that name already exists")
    else:
        os.mkdir("/tmp/video/" + brcd)

    return flst

def runconv(fullpath, convs):

   signal.signal(signal.SIGCHLD, signal.SIG_IGN)

   try:
       pid = os.fork()
       if pid > 0:
           pass
   except OSError, e:
       sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror)    )
       sys.exit(1)

   # Decouple from parent environment.
   if not pid:
      os.chdir("/")
      os.umask(0)
      os.setsid()

   # if we're the parent
   if pid:
       pass 

   else:

       convlst = genlist(fullpath, convs)
       #for i in range(len(convlst)): 
       #    outpath = convlst[i+len(convlst)/2]+'.flv'
       #    tResult = file('/tmp/video/' + outpath[14:], 'w')
       #    tResult.close()

       retVal = runchild('/dev/null', '/tmp/daemon.log', '/tmp/failure.log', convlst, pid) 
       # Child kills itself
       pgid = os.getpgid(pid)
       os.killpg(pgid, signal.SIGTERM)


def main(fullpath, convs):
   runconv(fullpath, convs)

if __name__ == '__main__':
   main(sys.argv[1], sys.argv[2])

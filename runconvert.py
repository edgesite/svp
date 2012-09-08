import signal, os, sys, time, fcntl, select, timeit, mimetypes, commands
import bfswalk, hasher, pymagic
    
def handler(signum, frame):
    print 'Alarm triggered after 30 seconds'
    os.popen2('killall python.bin')
    os.popen2('killall soffice')

class Runchild:

    def __init__(self, stdin, stdout, stderr, clst, tpid, curdir):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.convstr = clst
        self.pid = tpid
        self.curdir = curdir

    def runchild(self):

        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        convstr = self.convstr[:-5]
        convlst = convstr.split('$int$')
        pid = self.pid
        curdir = self.curdir

        so.write("<imageset barcode=\"%s\">\n" % curdir[6:])
        so.write("<tset>\n")

        # Additional exception handling needed
        for i in range(0, len(convlst)/2, 4):

            #signal.signal(signal.SIGALRM, handler)
            #signal.alarm(240)

            finlist = ['/l/openoffice.org2.2/program/python', '/u/kamwoods/Sudoc/svp/realtest/data/convert.py']

            if ((i + 4) > len(convlst)/2):
                finlist = finlist + convlst[i:len(convlst)/2]
                finlist = finlist + convlst[len(convlst)/2 + i:]
            else:
                finlist = finlist + convlst[i:i+4]   
                finlist = finlist + convlst[i+len(convlst)/2 : i + len(convlst)/2 + 4]   
        
            finlist.append('--format=PDF')

            #fin, so = os.popen2(finlist)
            try:
                fin, fout = os.popen2(finlist)
                for l in fout:
                    #signal.signal(signal.SIGALRM, handler)
                    #signal.alarm(240)
                    so.write(l)
                    #signal.alarm(0)
                #for l in fout.xreadlines():
                #    so.write(l) 
            except:
                continue            

            #signal.alarm(0)

        so.write("</tset>\n")        
        so.close()
        se.close()
        return 1

def genlist(fullpath, convs):
    # BFT for all images under current barcode, in order
    # if we're at the top level, do a gencnames for all images, appending lists together
    flst = []
    mlst = []
    curdir = fullpath.split("/")[-1]
    brcd = (fullpath.split("/")[3]).split("_")[1]

    # Only async (flag test)
    mconv = []
    for l in convs:
        if l[-1]:
            mconv.append(l)

    # Modified from internal
    # if len(curdir) > 6 and brcd == curdir[6:]:
    try:
        for f in os.listdir(fullpath):
            if not f.startswith('.'):
                # Generate list of all files
                for i in bfswalk.gencnames(os.path.join(fullpath, f)):
                    m = hasher.md5sum(i, mconv)
                    if not m == '-1':
                        typestr = mimetypes.guess_type(i)[0]
                        #if i[-3:].lower() == 'doc' and 
                        # commands.getoutput('file -i %s' % i).find('msword') == -1:
                        if i[-3:].lower() == 'doc' and pymagic.file(i).find('ASCII') > -1:
                            pass
                        else:
                            flst.append(i)
                            # Inconsistent - removal of PDF ending
                            mlst.append("/tmp/migrated/" + brcd + "/" + m[:-4])
    except:
        pass

    # Make one list, before we call the converter
    flst += mlst

    if len(flst) > 0:
        if os.path.isdir("/tmp/migrated/" + brcd):
            pass
        elif os.path.isfile("/tmp/migrated/" + brcd):
            raise OSError("a file with that name already exists")
        else:
            os.mkdir("/tmp/migrated/" + brcd)

    return flst

#def runconv(fullpath, convs):
def runconv(fullpath, convs):
   signal.signal(signal.SIGCHLD, signal.SIG_IGN)

   try:
       pid = os.fork()
       if pid > 0:
           pass
           #sys.exit(0)
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
       #pass   
       #sys.stderr.write("Parent got here with PID..." + str(pid) + "\n")
       #sys.stderr.write("Parent quitting..." + str(pid) + "\n")
       #sys.exit(0)
       pass
   else:
       # Generate file listing and make the appropriate directory
       #totals = {}
 
       ## Added second fork
       #try:
       #    pid = os.fork()
       #    if pid > 0:
       #        sys.stderr.write("Daemon initialized with pid..." + str(pid) + "\n")
       #        sys.exit(0)
       #except OSError, e:
       #    sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror)   )
       #    sys.exit(1)
       ## End second fork

       #for curdir in os.listdir('/mnt/isosrv/'):
       #for curdir in ['image_30000103442095']:
       #for curdir in ['image_30000103442079']:
       #convlst = genlist(os.path.join('/mnt/isosrv/', curdir), convs)
       sys.stderr.write("in runconv...")

       convlst = genlist(fullpath, convs)
       convstr = ''
       for x in convlst:
           convstr += x + '$int$'

       #sys.stderr.write(convstr)

       #signal.signal(signal.SIGALRM, handler)
       #signal.alarm(120)

       if len(convstr) > 0:
           #convstr = convstr[:-1]
           #t = timeit.Timer("R.runchild()", "from __main__ import Runchild; R = Runchild('/dev/null', '/tmp/daemon.log', '/tmp/failure.log', clst=\"%s\", tpid=%d, curdir='%s')" % (convstr, pid, curdir))
           R = Runchild('/dev/null', '/tmp/daemon.log', '/tmp/failure.log', convstr, pid, fullpath)
           retVal = R.runchild()
           sys.stderr.write("RETURNED FROM RUNCHILD: " + str(retVal))

           #dfile = open('/tmp/daemon.log', 'a')
           #dfile.write(convstr + '\n')
           #dfile.write("<time>%s</time>\n" % (str(t.timeit(1))))
           #dfile.write("</imageset>\n\n")
           #dfile.close()

       #signal.alarm(0)

       # Child kills itself
       sys.stderr.write("\nChild killed itself with killpg and PID: " + str(pid) + "\n")    
       pgid = os.getpgid(pid)
       os.killpg(pgid, signal.SIGTERM)

def main(fullpath, convs):
   runconv(fullpath, convs)

if __name__ == '__main__':
   main(sys.argv[1], sys.argv[2])
   #main(None, [['ppt','pdf',1],['wp','wp6','pdf',1]])
    #main(None, [['ppt','pdf',1],['doc','wrd','wri','wp','wp6','pdf',1]])
    #main('/mnt/isosrv/image_30000078832189', [['ppt','pdf',1],['doc','wrd','wri','wp','pdf',1]])


'''
 A module for getting information about .mdb (Microsoft Access Database)
 files.  The inputs are a filepath and an outpath.
'''

import os

def make_html(inpath, outpath):
    shd = os.popen2("mdb-tables -1 "+ inpath)
    tables = shd[1].readlines()
    shd2 = os.popen2("mdb-export " + inpath + " " + tables[0])
    try:
        data = shd2[1].readlines()[:10]
    except:
        data = shd2[1].readlines()
    shd[1].close()
    shd[0].close()
    shd2[1].close()
    shd2[0].close()

    f = open(outpath, "w")
 
    f.write("<html><head></head><body>")
    f.write("<h1>From file "+inpath.split('/')[-1]+"...</h1>")
    f.write("<h4>Tables in this file: <br></br>")
    for table in tables:
        f.write(str(table) + "<br>")
    f.write("<br> From table " + tables[0] + ":")
    f.write("<table>")
    for datum in data:
        datum = datum.split(',')
        f.write("<tr>")
        for element in datum:
            f.write("<td>"+element+"</td>")
        f.write("</tr>")
    f.write("</table>")
    f.write("</h4><br></br></body</html>")
    f.close()

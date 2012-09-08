import xlrd

'''
 make_html(inpath, outpath)
 The output of this will be a .html file version of the file at inpath at location outpath.
 This file will include a header with the number of worksheets, the name of
 the file, the column headers, and twenty-five lines of data from the first sheet.
'''

def make_html(inpath, outpath):

    file = xlrd.open_workbook(inpath)
    dest = open(outpath, 'w')
    
    dest.write("<html><head></head><body>")

    dest.write("<h3>From file " + inpath.split('/')[-1] + "...</h3>\n\n\n")
    dest.write("<h4>There are " + str(file.nsheets) + " worksheets in this file:\n")
    dest.write(str(file.sheet_names()) + "</h4>\n\n")
    sh = file.sheet_by_index(0)
    dest.write("<h4>From " + sh.name + "...</h4>\n")

    dest.write('<table border="1">')
    r = 0
    for row in range(sh.nrows):
        dest.write('<tr>')
        c = 0
        while c < sh.ncols:
            dest.write('<td width="10%">' + str(sh.cell_value(rowx=r, colx=c)) + "</td>\n")
            c += 1
        r += 1
        dest.write("</tr>\n")
        if r == 25:
            break
    dest.write("</table>")

    dest.close()

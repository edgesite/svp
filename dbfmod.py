# A set of classes to read FoxPro DBF files

import sys,string,struct

# --- Useful functions

def unpack_long(number):
    return ord(number[0])+256*(ord(number[1])+256*(ord(number[2])+\
                                                   256*ord(number[3])))

def unpack_long_rev(number):
    return ord(number[3])+256*(ord(number[2])+256*(ord(number[1])+\
                                                   256*ord(number[0])))

def unpack_int(number):
    return ord(number[0])+256*ord(number[1])

def unpack_int_rev(number):
    return ord(number[1])+256*ord(number[0])

def hex_analyze(number):
    for ch in number:
        print "%s\t%s\t%d" % (hex(ord(ch)),ch,ord(ch))

def sort_by_key(list,key_func):
    for ix in range(len(list)):
        list[ix]=(key_func(list[ix]),list[ix])

    list.sort()

    for ix in range(len(list)):
        list[ix]=list[ix][1]

    return list

# --- A class for the entire file

class DBFFile:
    "Represents a single DBF file."

    versionmap={"\x03":"dBASE III","\x83":"dBASE III+ with memo",
                "\x8B":"dBASE IV with memo","\xF5":"FoxPro with memo"}
    
    def __init__(self,filename):
        self.filename=filename
        try:
            self.blockfile=Blockfile(filename[:-4]+".fpt")
        except IOError:
            self.blockfile=None
        self._inspect_file()

    def _inspect_file(self):
        infile=open(self.filename,"rb")

        # Read header
        
        self.version=infile.read(1)
        infile.read(3)
        self.rec_num=unpack_long(infile.read(4))
        self.first_rec=unpack_int(infile.read(2))
        self.rec_len=unpack_int(infile.read(2))
        infile.read(20)

        # Read field defs

        self.fields={}
        while 1:
            ch=infile.read(1)
            if ch=="\x0D": break
            field=DBFField(ch+infile.read(31),self.blockfile)
            self.fields[field.name]=field
            
        infile.close()
    
    def get_version(self):
        return DBFFile.versionmap[self.version]

    def get_record_count(self):
        return self.rec_num

    def get_record_len(self):
        return self.rec_len

    def get_fields(self):
        return self.fields.values()

    def get_field(self,name):
        return self.fields[name]

    # --- Record-reading methods

    def open(self):
        self.infile=open(self.filename,"rb")
        self.infile.read(32+len(self.fields)*32+1)
        self.field_list=sort_by_key(self.get_fields(),DBFField.get_pos)

    def get_next_record(self):
        record={}
        ch=self.infile.read(1)
        if ch=="*":
            pass
            # Skip the record
            # return self.get_next_record() 
        elif ch=="\x1A" or ch=="":
            return None

        for field in self.field_list:
            record[field.get_name()]=field.interpret(self.infile.read(field.get_len()))

        return record
        
    def close(self):
        self.infile.close()
        del self.infile
    
# --- A class for a single field

class DBFField:
    "Represents a field in a DBF file."

    typemap={"C":"Character","N":"Numeric","L":"Logical","M":"Memo field",
             "G":"Object","D":"Date","F":"Float","P":"Picture"}
    
    def __init__(self,buf,blockfile):
        pos=string.find(buf,"\x00")
        if pos==-1 or pos>11: pos=11
        self.name=buf[:pos]
        self.field_type=buf[11]
        self.field_pos=unpack_long(buf[12:16])
        self.field_len=ord(buf[16])
        self.field_places=ord(buf[17])

        if self.field_type=="M" or self.field_type=="P" or \
           self.field_type=="G" :
            self.blockfile=blockfile

    def get_name(self):
        return self.name

    def get_pos(self):
        return self.field_pos
    
    def get_type(self):
        return self.field_type
    
    def get_type_name(self):
        return DBFField.typemap[self.field_type]

    def get_len(self):
        return self.field_len

    def interpret(self,data):
        if self.field_type=="C":
            return string.strip(data)
        elif self.field_type=="L":
            return data=="Y" or data=="y" or data=="T" or data=="t"
        elif self.field_type=="M":
            try:
                return self.blockfile.get_block(string.atoi(data)-8)
            except ValueError:
                return ""
        elif self.field_type=="N":
            try:
                return string.atoi(data)
            except ValueError:
                return 0
        elif self.field_type == "D":
            return data # string "YYYYMMDD", use the time module or mxDateTime
        else:
            raise NotImplementedError("Unknown data type " + self.field_type)
        
# --- A class that represents a block file

class Blockfile:
    "Represents a block file, either DBT or FPT."

    def __init__(self,filename):
        self.filename=filename

        infile=open(self.filename,"rb")
        infile.read(6)
        self.blocksize=unpack_int_rev(infile.read(2))
        infile.close()

    def get_block(self,number):
        infile=open(self.filename,"rb")
        infile.seek(512+self.blocksize*number)

        code=infile.read(4)
        if code!="\000\000\000\001":
            return "Block %d has invalid code %s" % (number,`code`)
        
        length=infile.read(4)
        length=unpack_long_rev(length)
        data=infile.read(length)        
        infile.close()

        return data

# --- A class that stores the contents of a DBF file as a hash of the
#     primary key

class DBFHash:

    def __init__(self,file,key):
        self.file=DBFFile(file)
        self.hash={}
        self.key=key

        self.file.open()
        while 1:
            rec=self.file.get_next_record()
            if rec==None: break
            self.hash[rec[self.key]]=rec

    def __getitem__(self,key):
        return self.hash[key]
            
# --- Utility functions

def display_info(f):
    print f.get_version()
    print f.get_record_count()
    print f.get_record_len()

    for field in f.get_fields():
        print "%s: %s (%d)" % (field.get_name(),field.get_type_name(),
                               field.get_len())

def make_html(f, out = sys.stdout, skiptypes = "MOP"):
    out.write("<HTML>\n<HEAD>\n</HEAD>\n<BODY>")    

    out.write("<TABLE>\n")

    # Writing field names
    out.write("<TR>")
    for field in f.get_fields():
        out.write("<TH>"+field.get_name()+"</TH>")
    out.write("</TR>")

    f.open()
    while 1:
        rec=f.get_next_record()
        if rec==None: break

        out.write("<TR>")
        for field in f.get_fields():
            if not field.get_type() in skiptypes:
                out.write("<TD>"+str(rec[field.get_name()])+"</TD>")
            else:
                out.write("<TD>*skipped*"+"</TD>")
        out.write("</TR>\n")

    f.close()
    out.write("</TABLE>\n") 

    out.write("</BODY>\n</HTML>\n")

def make_list_lim(f, out = sys.stdout, skiptypes = "MOP"):
    out.write("<HTML>\n<HEAD>\n</HEAD>\n<BODY>")    

    out.write("<TABLE>\n")

    # Writing field names
    out.write("<TR>")

    for field in f.get_fields():
        out.write("<TH>"+field.get_name())

    f.open()
    count = 0
    while count < 100:
        rec=f.get_next_record()
        if rec==None: break

        out.write("<TR>")
        for field in f.get_fields():
            if not field.get_type() in skiptypes:
                out.write("<TD>"+str(rec[field.get_name()]) + "</TD>")
            else:
                out.write("<TD>*skipped*" + "</TD>") 
        count = count + 1
        out.write("</TR>\n")

    f.close()
    out.write("</TABLE>\n") 

    out.write("</BODY>\n</HTML>\n")

if __name__ == "__main__":
    make_list_lim(DBFFile(sys.argv[1]))
    #make_html(DBFFile(sys.argv[1]))
    #pass

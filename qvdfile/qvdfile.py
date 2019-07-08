
import os, datetime, time
from bitstring import BitArray, BitStream, pack

from qvdfile.xml2dict import xml2dict

class BadFormat(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class QvdFile():

    def __init__(self,name):

        """ QvdFile object has two mutually exclusive modes - we either read existing file or create new one
        During init we determine what mode we are in and for that we use file extension:
        
        - if it is ".qvd" then we are reading
        - if it is ".xml" then we are creating new QVD file with the stucture defined in XML 

        XML file has exactly the same structure as metadata section of QVD file, there is a tool
        which extracts metadata section from QVD file and clears necessary data (e.g. number of rows is unknown), 
        this tool is also capable of creating XML template with just one field. """

        self.mode = os.O_RDONLY if os.path.split(name)[1].split('.')[1].lower()=='qvd' else os.O_WRONLY

        """ We never ever want to erase exisitng QVD file, so we check QVD file presence and raise
        exception if it exists """
        
        if self.mode==os.O_WRONLY and os.access(name.split('.')[0]+'.qvd',os.R_OK): 
            raise FileExistsError
        
        f = os.open(name,os.O_RDONLY)
        bta = bytearray()
        buf = os.read(f,100000)
        while buf: # read file in chunks, looking for end of metadata
            bta.extend(buf)
            if buf.find(b'</QvdTableHeader>')>0:
                break
            buf = os.read(f,100000)
        else: # malformed QVD file, raise exception
            raise BadFormat

        buf = bytes(bta)
        
        self.fName = name
        if self.mode==os.O_RDONLY:
            self.fp = f # we need QVD file to be opened - we are going to read from it
        else: # in the case of creating new QVD we do not need XML eny longer
            self.fp = None
            f.close()
        
        # form metadata bytes
        xml = buf.split(b'</QvdTableHeader>')[0] + b'\n</QvdTableHeader>'

        if self.mode==os.O_RDONLY:
            self.stPos = len(xml)
            self.xml = None # do not need XML in case of reading
            # there might be some symbols in the end of metadata - skip them
            os.lseek(f,self.stPos,0) 
            while True:
                b = os.read(f,1)
                if b not in [ b'\r', b'\n', b'\0']:
                    break
                self.stPos += 1
        else:
            self.xml = xml # save metadata - we need them for the metadata section (in the case of creating new QVD)
            self.stPos = 0 # this will be known at the moment of writing file, now just something

        # convert XML to dict and add "shortcuts"
        self.root = xml2dict(b'<QvdTableHeader>'+xml.split(b'<QvdTableHeader>')[1])
        self.attribs = self.root["QvdTableHeader"] # dict of attributes - save some typing
        self.fields = self.root["QvdTableHeader"]["Fields"]["QvdFieldHeader"] # list of fields - save typing

        # some configurable staff
        self.NoneValueStr = "(None)" # value of the field with 0 values (if requested)

    def getFieldVal(self,fName,vInd):
        """ get field value as string
        fName is field as (as is in Metedata)
        vInd is field value index (zero bases)
        
        raises IndexError in case vInd is larger then field value number
        raises KeyEror in case fName is not a valid field name
        """

        # get field object
        for f in self.fields:
            if f["FieldName"]==fName:
                fld = f
                break
        else:
            raise KeyError  

        if f["NoOfSymbols"]=="0": # this effectively means None...
            return self.NoneValueStr

        # check value index range
        if vInd>=int(f["NoOfSymbols"]):
            raise IndexError
        
        # read data sequentially
        os.lseek(self.fp,self.stPos+int(f["Offset"]),os.SEEK_SET) # seek to symbol table beginning
        for i in range(vInd+1):
            # read field type byte
            b = ord(os.read(self.fp,1))

            # read value
            if b in [4,5,6]: # string containing types
                if b in [5,6]: # skip numeric value
                    skipSize = 4 if b==5 else 8 # byte size to skip
                    smth = os.lseek(self.fp,skipSize,os.SEEK_CUR) 
                    
                val = b''
                while True: # have to read bytewise - very ineffective
                    bt = os.read(self.fp,1)
                    if bt==b'\0':
                        break
                    val += bt
                val = val.decode("utf-8") # string is always UTF-8
                                
            elif b in [1,2]: # numeric types
                a = BitArray(os.read(self.fp,b*4))
                if b==1:
                    val = a.unpack("intle:32")[0]
                else:
                    val = a.unpack("floatle:64")[0]
                                                
            else:
                print ("UNHANDLED YET TYPE: ", b) # never happened to me...
                                               
        return val

    def fieldsInRow(self):
        """ generator function which iterates over the fields in the order
        they are placed in the bit index of row table - field with 0 offset
        is the rightmost one. So generator will first returm leftmost field,
        rightmost field (with 0 offset) will be the last one :-)

        Generator skips fields with 0 width - there no such fields in bit index
        """
        for f in sorted(self.fields, key=lambda k: int(k['BitOffset']), reverse=True):
            if f["BitWidth"]=="0":
                continue
            yield f
        
    def createMask(self):
        """ returns mask for bitstring processing 
        using BitString module's BitArray functionality
        and will be used like this:

            bitarray.unpack(mask)

        rightmost byte in bitearray is that for the field with 0 offset.
        
        Mask is always uint - we are dealing with symbol table indices (non negative).

        Mask always contains full bytes (this is handled via BitWidth values).
        """

        mLst = []
        for f in self.fieldsInRow():
            mLst.append("uint:{}".format(f["BitWidth"]))
                
        return ",".join(mLst) # mask in bitstring format

    def getRow(self,rInd): 
        """ returns row as dictionary
        values are always strings, index is 0 based

        Bytes in the file are in reversed order, keep this in mind when processing 
        
        raises IndexError in case rInd is larger then row number
        """

        # check row index range
        if rInd>=int(self.attribs["NoOfRecords"]):
            raise IndexError

        # seek to the rows table beginning
        os.lseek(self.fp,
                 self.stPos + int(self.attribs["Offset"]) + int(self.attribs["RecordByteSize"])*rInd,
                 os.SEEK_SET) 

        bts = bytearray(os.read(self.fp,int(self.attribs["RecordByteSize"])))

        bts.reverse() # bytes are reversed in file
        ba = BitArray(bts) # very slow operation btw
        indList = ba.unpack(self.createMask()) # make list
            
        # create resulting dictionary
        res = {}
        # add fields with more than one value
        for fInd,f in enumerate(self.fieldsInRow()):
            symInd = indList[fInd] + int(f["Bias"]) # always add bias - it is 0 or -2
            val = self.NoneValueStr if symInd<0 else self.getFieldVal(f["FieldName"],symInd) # NULL correction
            res[f["FieldName"]] = val

        # add fields with one value
        for cf in [f for f in self.fields if f["BitWidth"]=="0"]: # we use BitWidth, will elaborate later (there are cases...)
            res[cf["FieldName"]] = self.getFieldVal(cf["FieldName"],0)

        return res


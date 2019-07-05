# qvdfile

## QVD File reader and writer (exploratory version)

This is python object created to explore QVD file, it can be used 

* to read QVD file Metedata
* to read column values from QVD file
* to read rows from QVD file

Sample usage:

```
import qvdfile 

qvd = QvdFile ("test.qvd")

print("File has {} records".format(qvd.attribs["NumberOfRecords"]))

print("File has column '{}' with first value of '{}'".format(
  qvd.fields[0]["FieldName"],qvd.getFieldValue(qvd.fields[0]["FieldName"],0)))
  
print("First row of the file is {}".format(qvd.getRow(0)))
```

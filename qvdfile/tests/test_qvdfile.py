import pytest
import errno
import os
import glob
import shutil

import xml.etree.ElementTree as ET

from qvdfile.qvdfile import QvdFile, BadFormat

@pytest.fixture(scope="function")
def qvd():
    """ standard setup for most of the tests """

    yield QvdFile("data/tab1.qvd")

@pytest.fixture(scope="function")
def bigqvd():
    """ standard setup for tests with bigger qvd"""

    yield QvdFile("data/tab2.qvd")
    
# READING QVD ==================================================================

# init

def test_init_smoke(qvd):

    # metadata is in attribs
    assert "TableName" in qvd.attribs.keys()
    assert qvd.attribs["TableName"] == "tab1"

    # fields info is in fields
    assert len(qvd.fields) == 3
    assert "ID" in [ f["FieldName"] for f in qvd.fields ]

def test_init_no_file():
    
    with pytest.raises(FileNotFoundError):
        qvd = QvdFile("data/no_such_file.qvd")

def test_init_not_qvd_or_bad_file():
        
    with pytest.raises(BadFormat):
        qvd = QvdFile(__file__)

# getFieldVal

def test_get_field_val_smoke(qvd):

    assert qvd.getFieldVal("ID",0) == "123.12"
    assert qvd.getFieldVal("NAME",2) == "Vaysa"
    assert qvd.getFieldVal("ONEVAL",0) == "0"
    
def test_get_field_val_bad_name(qvd):

    with pytest.raises(KeyError):
        qvd.getFieldVal("NOFILED",0) 

def test_get_field_val_bad_index(qvd):

    with pytest.raises(IndexError):
        qvd.getFieldVal("ID",10) 

# fieldsInRow

def test_fields_in_row_smoke(qvd):

    rowf = qvd.fieldsInRow()
    
    assert next(rowf)["FieldName"] == "NAME"
    assert next(rowf)["FieldName"] == "ID"
    with pytest.raises(StopIteration):
        next(rowf) 

def test_fields_in_row_bigger(bigqvd):

    rowf = bigqvd.fieldsInRow()
    
    assert next(rowf)["FieldName"] == "NAME"
    assert next(rowf)["FieldName"] == "PHONE"
    assert next(rowf)["FieldName"] == "VAL"
    assert next(rowf)["FieldName"] == "ID"
    with pytest.raises(StopIteration):
        next(rowf) 

# createMask

def test_create_mask_smoke(qvd):
    
    assert qvd.createMask() == "uint:5,uint:3"

def test_create_mask_bigger(bigqvd):
    
    assert bigqvd.createMask() == "uint:6,uint:5,uint:5,uint:8"
    
# getRow

def test_get_row_smoke(qvd):

    row = qvd.getRow(0)
    
    assert row["ID"] == "123.12"
    assert row["NAME"] == "Pete"
    assert row["ONEVAL"] == "0"    

def test_get_row_bad_index(qvd):

    with pytest.raises(IndexError):
        qvd.getRow(10) 

def test_get_row_null(qvd):

    row = qvd.getRow(4)
    
    assert row["ID"] == qvd.NoneValueStr

def test_get_row_bigger(bigqvd):

    row = bigqvd.getRow(0)
            
    assert row["ID"] == "1"
    assert row["VAL"] == "100001"
    assert row["NAME"] == "Pete1"    
    assert row["PHONE"] == "1234567890"    
    assert row["SINGLE"] == "single value"    

def test_get_row_bigger_nulls(bigqvd):

    row = bigqvd.getRow(17)
            
    assert row["ID"] == "-18"
    assert row["VAL"] == bigqvd.NoneValueStr
    assert row["NAME"] == "Pete17"    
    assert row["PHONE"] == bigqvd.NoneValueStr
    assert row["SINGLE"] == "single value"    
    
# WRITING QVD ===================================================================

# code and tests will follow....

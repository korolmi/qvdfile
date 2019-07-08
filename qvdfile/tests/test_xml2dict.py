import pytest
import xml.etree.ElementTree as ET

from qvdfile.xml2dict import xml2dict

def test_xml2dict_smoke():
    """ Simple smoke test - just an example """

    xml = """
<root>
    <tag1>1</tag1>
    <nested>
       <tagn>111</tagn>
       <tagn>222</tagn>
    </nested>
</root>"""

    d = xml2dict(xml)
    
    # root
    assert len(d.items()) == 1
    assert "root" in d.keys()

    # first level
    assert len(d["root"].items()) == 2
    assert "tag1" in d["root"].keys()
    assert "nested" in d["root"].keys()
    assert d["root"]["tag1"] == '1'

    # second level
    assert len(d["root"]["nested"].items()) == 1
    assert "tagn" in d["root"]["nested"].keys()
    assert len(d["root"]["nested"]["tagn"]) == 2
    assert d["root"]["nested"]["tagn"][0] == '111'
    assert d["root"]["nested"]["tagn"][1] == '222'

def test_xml2dict_empty():
    """ working with empty XML """

    xml = " \t\n"

    d = xml2dict(xml)

    # empty dict
    assert type(d) is dict
    assert len(d.items()) == 0

def test_xml2dict_value_is_string():
    """ every value in result is string """

    xml = "<tag>1</tag>"

    d = xml2dict(xml)

    assert type(d["tag"]) is str

def test_xml2dict_value_is_striped():
    """ values in result are stripped """

    xml = "<tag>\t1 \n</tag>"

    d = xml2dict(xml)

    assert d["tag"] == "1"

def test_xml2dict_tag_is_case_sensitive():
    """ tags are case sensitive """

    xml = "<tag>1</tag>"

    d = xml2dict(xml)

    assert "tag" in d.keys()
    assert "TAG" not in d.keys()
    
def test_xml2dict_value_is_case_sensitive():
    """ values are of course case sensitive """

    xml = "<tag>Val</tag>"

    d = xml2dict(xml)

    assert d["tag"] == "Val"

def test_xml2dict_invalid_xml():
    """ invalid XML raises ParseError """

    xml = "<tag>1</ta>"

    with pytest.raises(ET.ParseError):
        d = xml2dict(xml)

def test_xml2dict_real():
    """ we are dealing with XML from QVD file - here is shortened example just to show real things """

    xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<QvdTableHeader>
    <QvBuildNo>7314</QvBuildNo>
    <Fields>
     <QvdFieldHeader>
       <FieldName>ID</FieldName>
     </QvdFieldHeader>
     <QvdFieldHeader>
       <FieldName>NAME</FieldName>
     </QvdFieldHeader>
    </Fields>
</QvdTableHeader>"""
    
    d = xml2dict(xml)

    assert d["QvdTableHeader"]["Fields"]["QvdFieldHeader"][0]["FieldName"] == "ID"
    assert d["QvdTableHeader"]["Fields"]["QvdFieldHeader"][1]["FieldName"] == "NAME"
    

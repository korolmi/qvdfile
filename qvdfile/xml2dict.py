"""

Converts XML tree to dictionary, see unit tests for usage examples

Simplified to work with QVD XML, do not try to use for general XML to dictionary conversion.

"""

import xml.etree.ElementTree as ET
from collections import defaultdict

def xml2dict( sXml ):
    """ converts XML string to dictionary """

    if sXml.strip():
        return etree2dict(ET.fromstring(sXml))
    else:
        return dict()

def etree2dict( t ):
    """ recursive tree converter """
    
    d = {t.tag: None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree2dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.text and t.text.strip():
        d[t.tag] = t.text.strip()
        
    return d

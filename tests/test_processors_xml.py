import os
from lxml.etree import _ElementTree
from sandhill.processors import xml
from sandhill import app

def test_xml_load():
    data_str = {
        'source': '<main><str>one</str><str>two</str></main>'
    }
    data_missing = {
    }

    # Load unicode string
    doc = xml.load(data_str)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == 'main'
    child_tags = [t.tag for t in doc.getroot()]
    assert child_tags == ['str', 'str']

    # Missing source tag 
    doc = xml.load(data_missing)
    assert doc is None

def test_xml_xpath():
    data_str = {
        'source': '<main><str>one</str><str>two</str></main>',
        'xpath': '/main/str'
    }
    data_nopath = {
        'source': '<main><str>one</str><str>two</str></main>',
    }

    matched = xml.xpath(data_str)
    assert isinstance(matched, list)
    assert len(matched) == 2

    matched = xml.xpath(data_nopath)
    assert matched is None

def test_xml_xpath_by_id():
    data_str = {
        'source': '<main><str id="one">One</str><str id="two"><p>Two</p></str></main>',
        'xpath': '/main/str'
    }
    data_nopath = {
        'source': '<main><str>one</str><str>two</str></main>',
    }

    idmap = xml.xpath_by_id(data_str)
    assert isinstance(idmap, dict)
    assert list(idmap.keys()) == ['one', 'two']
    assert idmap['one'] == "One"
    assert idmap['two'] == "<p>Two</p>"

    matched = xml.xpath_by_id(data_nopath)
    assert matched is None

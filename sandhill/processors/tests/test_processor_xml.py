import os
from lxml.etree import _ElementTree
from sandhill.processors import xml
from sandhill import app

def test_xml_load():
    data_bin = {
        'source': b'<main><el>one</el><el>two</el></main>'
    }
    data_str = {
        'source': '<main><str>one</str><str>two</str></main>'
    }
    data_file = {
        'source':  os.path.join(app.instance_path, 'xml_files/example1.xml')
    }
    data_url = {
        'source': 'https://www.wikidata.org/wiki/Special:EntityData/Q6750239.rdf'
    }
    data_unknown = {
        'source': 'This is not XML, a file, or a URL'
    }
    data_badxml = {
        'source': '<main><str>one</str><str>two</str></badend>'
    }
    data_missing = {
    }
    data_badhost = {
        'source': 'https://domain.does.not.exist.testing/'
    }
    data_badreq = {
        'source': 'https://www.wikidata.org/wiki/Special:EntityData/TEST.rdf'
    }

    # Load bytes
    doc = xml.load(data_bin)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == 'main'

    # Load unicode string
    doc = xml.load(data_str)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == 'main'
    child_tags = [t.tag for t in doc.getroot()]
    assert child_tags == ['str', 'str']

    # Load local file
    doc = xml.load(data_file)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == 'items'
    child_tags = [t.tag for t in doc.getroot()]
    assert 'content' in child_tags
    assert len(child_tags) == 3

    # Load from remote URL
    doc = xml.load(data_url)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'
    child_tags = [t.tag for t in doc.getroot()]
    assert '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description' in child_tags

    # Unknown source data
    doc = xml.load(data_unknown)
    assert doc is None

    # Missing source tag 
    doc = xml.load(data_missing)
    assert doc is None

    # Invalid XML
    doc = xml.load(data_badxml)
    assert doc is None

    # Request to bad host
    doc = xml.load(data_badhost)
    assert doc is None

    # Non HTTP 200 response (or timeout)
    doc = xml.load(data_badreq)
    assert doc is None

def test_xml_xpath():
    data_str = {
        'source': '<main><str>one</str><str>two</str></main>',
        'xpath': '/main/str'
    }
    data_badq = {
        'source': '<main><str>one</str><str>two</str></main>',
        'xpath': 'NOT a valid xpath!!'
    }

    matched = xml.xpath(data_str)
    assert isinstance(matched, list)
    assert len(matched) == 2

    matched = xml.xpath(data_badq)
    assert matched is None

def test_xml_xpath_by_id():
    data_str = {
        'source': '<main><str id="one">One</str><str id="two"><p>Two</p></str></main>',
        'xpath': '/main/str'
    }

    idmap = xml.xpath_by_id(data_str)
    assert isinstance(idmap, dict)
    assert list(idmap.keys()) == ['one', 'two']
    assert idmap['one'] == "One"
    assert idmap['two'] == "<p>Two</p>"

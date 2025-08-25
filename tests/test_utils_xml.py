import os
from lxml.etree import _ElementTree
from sandhill.utils import xml
from sandhill import app

def test_utils_xml_load():
    source_bin = b'<main><el>one</el><el>two</el></main>'
    source_str = '<main><str>one</str><str>two</str></main>'
    source_file = os.path.join(app.instance_path, 'xml_files/example1.xml')
    source_url = 'https://catalog.lib.msu.edu/Record/folio.in00001735688/Export?style=RDF'
    source_unknown = 'This is not XML, a file, or a URL'
    source_badxml = '<main><str>one</str><str>two</str></badend>'
    source_badhost = 'https://domain.does.not.exist.testing/'
    source_badreq = 'https://www.wikidata.org/wiki/Special:EntityData/TEST.rdf'

    # Load bytes
    doc = xml.load(source_bin)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == 'main'

    # Load unicode string
    doc = xml.load(source_str)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == 'main'
    child_tags = [t.tag for t in doc.getroot()]
    assert child_tags == ['str', 'str']

    # Load local file
    doc = xml.load(source_file)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == 'items'
    child_tags = [t.tag for t in doc.getroot()]
    assert 'content' in child_tags
    assert len(child_tags) == 3

    # Load from remote URL
    doc = xml.load(source_url)
    assert isinstance(doc, _ElementTree)
    assert doc.getroot().tag == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF'
    child_tags = [t.tag for t in doc.getroot()]
    assert '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description' in child_tags

    # Unknown source data
    doc = xml.load(source_unknown)
    assert doc is None

    # Invalid XML
    doc = xml.load(source_badxml)
    assert doc is None

    # Request to bad host
    doc = xml.load(source_badhost)
    assert doc is None

    # Non HTTP 200 response (or timeout)
    doc = xml.load(source_badreq)
    assert doc is None

    # Not string or bytes
    doc = xml.load(3.14)
    assert doc is None

def test_utils_xml_xpath():
    source_str = '<main><str>one</str><str>two</str></main>'
    source_elem = xml.load(source_str)
    xpath_str = '/main/str'
    xpath_badq = 'NOT a valid xpath!!'

    matched = xml.xpath(source_str, xpath_str)
    assert isinstance(matched, list)
    assert len(matched) == 2

    matched = xml.xpath(source_elem, xpath_str)
    assert isinstance(matched, list)
    assert len(matched) == 2

    matched = xml.xpath(source_str, xpath_badq)
    assert matched is None

def test_utils_xml_xpath_by_id():
    source_str = '<main><str id="one">One</str><str id="two"><p>Two</p></str></main>'
    source_bin = b'<main><str id="one">One</str><str id="two"><p>Two</p>Tail</str></main>'
    source_elem = xml.load(source_str)
    xpath = '/main/str'

    idmap = xml.xpath_by_id(source_str, xpath)
    assert isinstance(idmap, dict)
    assert list(idmap.keys()) == ['one', 'two']
    assert idmap['one'] == "One"
    assert idmap['two'] == "<p>Two</p>"

    idmap = xml.xpath_by_id(source_bin, xpath)
    assert isinstance(idmap, dict)
    assert list(idmap.keys()) == ['one', 'two']
    assert idmap['one'] == "One"
    assert idmap['two'] == "<p>Two</p>Tail"

    idmap = xml.xpath_by_id(source_elem, xpath)
    assert isinstance(idmap, dict)
    assert list(idmap.keys()) == ['one', 'two']

    idmap = xml.xpath_by_id(None, xpath)
    assert idmap is None

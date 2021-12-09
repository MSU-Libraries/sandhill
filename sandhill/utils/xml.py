import io
from lxml import etree
import requests
from requests.exceptions import ConnectionError
from validator_collection import checkers
from sandhill import app, catch

@catch(etree.XMLSyntaxError, "Invalid XML source: {source} Exc: {exc}", return_val=None)
@catch(ConnectionError, "Invalid host in XML call: {source} Exc: {exc}", return_val=None)
def load(source) -> etree._Element:
    '''
    Load an XML document
    args:
        source: XML source. Either path, url, or string
    returns:
        Loaded XML object tree
    '''
    if isinstance(source, etree._ElementTree):
        return source

    source = source.strip()
    if source[0] == ord('<'):           # Handle source as bytes
        source = io.BytesIO(source)
    elif source[0] == '<':              # Handle source as string
        source = io.StringIO(source)
    elif checkers.is_file(source):      # Handle source as local file
        pass  # etree.parse handles local file paths natively
    elif checkers.is_url(source):       # Handle source as URL
        response = requests.get(source, timeout=10)
        if not response:
            app.logger.warning(f"Failed to retrieve XML URL (or timed out): {source}")
            return None
        source = io.BytesIO(response.content)
    else:
        app.logger.warning(f"XML source is not valid file, URL, or XML string. {source[:40]}"
                           + (len(source) > 40) * '...')
        return None

    return etree.parse(source)

@catch(etree.XPathEvalError, "Invalid XPath query {query} Exc {exc}", return_val=None)
def xpath(source, query) -> list:
    '''
    Retrieve the matching xpath content from an XML source
    args:
        query: XPath query to match against
        source: XML source. Either path, url, or string
    returns:
        Matching results from XPath query
    '''
    doc = load(source)
    return doc.xpath(query, namespaces=doc.getroot().nsmap)

def xpath_by_id(source, query) -> dict:
    '''
    For the matching xpath content, organize into dict with key
    being the id param of the matched tags. Elements without an id attribute
    will not be returned.
    args:
        query: XPath query to match against
        source: XML source. Either path, url, or string
    returns:
        Dict mapping with keys of id, and values of content within matching elements
    '''
    matched = xpath(source, query)

    idmap = {}
    for match in matched:
        if 'id' in match.keys():
            text = match.text if match.text is not None else ''
            for elem in match.iterchildren():
                text += etree.tostring(elem, encoding='unicode')
            text += match.tail if match.tail is not None else ''
            idmap[match.get('id')] = text
    return idmap

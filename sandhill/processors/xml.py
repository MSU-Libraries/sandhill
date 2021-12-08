import io
from xml.etree import ElementTree
from lxml import etree
import requests
from requests.exceptions import ConnectionError
from validator_collection import checkers
from sandhill import app, catch

@catch(etree.XMLSyntaxError, "Invalid XML source: {data_dict[source]} Exc: {exc}", return_val=None)
@catch(ConnectionError, "Invalid host in XML call: {data_dict[source]} Exc: {exc}", return_val=None)
def load(data_dict: dict) -> ElementTree:
    '''
    Load an XML document
    args:
        data_dict: Dict with keys
            'source': XML source. Either path, url, or string
    returns:
        Loaded XML object tree
    '''
    if 'source' not in data_dict:
        app.logger.warning("No source XML provided. Missing key: 'source'")
        return None

    source = data_dict['source'].strip()
    if source[0] == ord('<'):               # Handle source as bytes
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

@catch(etree.XPathEvalError, "Invalid XPath query {data_dict[xpath]} Exc {exc}", return_val=None)
def xpath(data_dict: dict) -> list:
    '''
    Retrieve the matching xpath content from an XML source
    args:
        data_dict: Dict with keys
            'xpath': XPath to try to match
            'source': XML source. Either path, url, or string
    returns:
        Matching results from XPath query
    '''
    if 'xpath' not in data_dict:
        app.logger.warning("No xpath search provided. Missing key: 'xpath'")
        return None

    doc = load(data_dict)
    return doc.xpath(data_dict['xpath'], namespaces=doc.getroot().nsmap)

    #print(f"Found {len(results)} results.")
    #for r in results:
    #    print(f"Tag: {r.tag}")
    #    print(f"Text: {etree.tostring(r)}")

def xpath_by_id(data_dict: dict) -> dict:
    '''
    For the matching xpath content, organize into dict with key
    being the id param of the matched tags. Elements without an id attribute
    will not be returned.
    args:
        data_dict:
            'xpath': XPath to try to match
            'source': XML source. Either path, url, or string
    returns:
        Dict mapping with keys of id, and values of content within matching elements
    '''
    matched = xpath(data_dict)

    idmap = {}
    for match in matched:
        print(f"ID: {match['id']}")
        if 'id' in match:
            idmap[match.get('id')] = etree.tostring(match)
    return idmap

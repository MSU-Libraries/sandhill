'''
XML loading and handling
'''
import io
from lxml import etree
import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from validator_collection import checkers
from sandhill import app, catch

@catch(etree.XMLSyntaxError, "Invalid XML source: {source} Exc: {exc}", return_val=None)
@catch(RequestsConnectionError, "Invalid host in XML call: {source} Exc: {exc}", return_val=None)
def load(source) -> etree._Element: # pylint: disable=protected-access
    '''
    Load an XML document
    args:
        source: XML source. Either path, url, string, or loaded LXML Element
    returns:
        Loaded XML object tree, or None on invalid source
    '''
    if not isinstance(source, (str, bytes)) or len(source) < 1:
        # pylint: disable=protected-access
        return source if isinstance(source, etree._ElementTree) else None

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
        Matching results from XPath query, or None on failure
    '''
    doc = load(source)
    return doc.xpath(query, namespaces=doc.getroot().nsmap) if doc else None

def xpath_by_id(source, query) -> dict:
    '''
    For the matching xpath content, organize into dict with key
    being the id param of the matched tags. Elements without an id attribute
    will not be returned.
    args:
        query: XPath query to match against
        source: XML source. Either path, url, or string
    returns:
        Dict mapping with keys of id, and values of content within matching elements,
        or None on failure
    '''
    matched = xpath(source, query)
    if matched is None: # Explicit check to avoid empty results being matched
        return None

    idmap = {}
    for match in matched:
        if 'id' in match.keys():
            text = match.text if match.text is not None else ''
            for elem in match.iterchildren():
                text += etree.tostring(elem, encoding='unicode')
            text += match.tail if match.tail is not None else ''
            idmap[match.get('id')] = text
    return idmap

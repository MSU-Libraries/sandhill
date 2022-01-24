'''
XML Data Processors
'''
from lxml import etree
from sandhill import app
from sandhill.utils import xml


def load(data: dict) -> etree._Element: # pylint: disable=protected-access
    '''
    Load an XML document
    args:
        data: Dict with keys
            'source': XML source. Either path, url, or string
    returns:
        Loaded XML object tree
    '''
    if 'source' not in data:
        app.logger.warning("No source XML provided. Missing key: 'source'")
        return None
    return xml.load(data['source'])

def xpath(data: dict) -> list:
    '''
    Retrieve the matching xpath content from an XML source
    args:
        data: Dict with keys
            'xpath': XPath to try to match
            'source': XML source. Either path, url, or string
    returns:
        Matching results from XPath query
    '''
    if 'xpath' not in data:
        app.logger.warning("No xpath search provided. Missing key: 'xpath'")
        return None
    return xml.xpath(load(data), data['xpath'])

def xpath_by_id(data: dict) -> dict:
    '''
    For the matching xpath content, organize into dict with key
    being the id param of the matched tags. Elements without an id attribute
    will not be returned.
    args:
        data:
            'xpath': XPath to try to match
            'source': XML source. Either path, url, or string
    returns:
        Dict mapping with keys of id, and values of content within matching elements
    '''
    if 'xpath' not in data:
        app.logger.warning("No xpath search provided. Missing key: 'xpath'")
        return None
    return xml.xpath_by_id(load(data), data['xpath'])

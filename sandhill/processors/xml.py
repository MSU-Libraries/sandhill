'''
XML Data Processors
'''
from lxml import etree
from sandhill import app
from sandhill.utils import xml


def load(data: dict) -> etree._Element: # pylint: disable=protected-access
    '''
    Load an XML document.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `source` _str_: Either path, url, or string to load.\n
    Returns:
        (lxml.etree._Element|None): The loaded XML object tree, or None if `source` not in data.
    '''
    if 'source' not in data:
        app.logger.warning("No source XML provided. Missing key: 'source'")
        return None
    return xml.load(data['source'])

def xpath(data: dict) -> list:
    '''
    Retrieve the matching xpath content from an XML source.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `xpath` _str_: An XPath query.\n
            * `source` _str_: Either path, url, or string to load.\n
    Returns:
        (list): Matching results from XPath query, or None if any required keys are not in data.
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
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `xpath` _str_: An XPath query.\n
            * `source` _str_: Either path, url, or string to load.\n
    Returns:
        (dict): Dict mapping with keys of id, and values of content within matching elements, \
            or None if missing any required keys in data.
    '''
    if 'xpath' not in data:
        app.logger.warning("No xpath search provided. Missing key: 'xpath'")
        return None
    return xml.xpath_by_id(load(data), data['xpath'])

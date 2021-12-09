"""Filters for jinja templating engine"""
import urllib
import re
import html
from collections.abc import Hashable
from datetime import datetime
import mimetypes
from ast import literal_eval
import copy
from jinja2 import contextfilter, TemplateError
from markupsafe import Markup
from sandhill import app, catch
from sandhill.utils.generic import get_config
from sandhill.utils.solr import Solr
from sandhill.utils.html import HTMLTagFilter
from sandhill.utils import xml

@app.template_filter('size_format')
def size_format(value):
    """Jinja filter to format the binary size"""
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    nbytes = int(value) if f"{value}".isdigit() else 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024
        i += 1
    fsize = ('%.1f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (fsize, suffixes[i])

@app.template_filter('is_list')
def is_list(value):
    """Check if a value is a list"""
    return isinstance(value, list)

@app.template_filter('get_extension')
def get_extension(value):
    """Take in mimetype and return extension."""
    mimetypes.add_type("audio/wav", '.wav')
    extension = None
    preferred = [".txt", ".jpg", ".mp3"]
    all_extensions = mimetypes.guess_all_extensions(value)
    if all_extensions:
        for ext in all_extensions:
            if ext in preferred:
                extension = ext
                break
        if not extension:
            extension = all_extensions[0]
    else:
        extension = ".???"
    return extension.upper()[1:]

@app.template_filter('head')
def head(value):
    """Returns the head of the list if non-empty list, otherwise the orig value"""
    if isinstance(value, list) and value:
        value = value[0]
    return value

@app.template_filter('unescape')
def unescape(value):
    """Unescape special characters in a string of HTML"""
    return html.unescape(value)

@app.template_filter('filter_tags')
def filter_tags(value, *args):
    """Filter out all HTML tags except for the ones specified
    and marks the output as safe to render."""
    htf = HTMLTagFilter(allow=args)
    htf.feed(value)
    return Markup(htf.output)

@app.template_filter('solr_encode_query')
def solr_encode_query(query, escape_wildcards=False):
    """
    Parses and encodes Solr queries (the part after the colon)
    args:
        query (str): Solr query to encode
        escape_wildcards(bool): If Solr's wildcard indicators (* and ?)
            should be encoded (Default: False)
    returns:
        (str): The solr query with appropriate characters encoded
    """
    return Solr().encode_query(query, escape_wildcards=escape_wildcards)

@app.template_filter('solr_encode')
def solr_encode(value, escape_wildcards=False):
    """Filter to encode a value being passed to Solr
    args:
        value (str): string to escape Solr characters
        escape_wildcards(bool): If Solr's wildcard indicators (* and ?)
            should be encoded (Default: False)
    returns:
        (str): same string but with Solr characters encoded
    """
    if isinstance(value, str):
        value = Solr().encode_value(value, escape_wildcards)
    return value

@app.template_filter('solr_decode')
def solr_decode(value, escape_wildcards=False):
    """Filter to decode a value previously encoded for Solr
    args:
        value (str): string with Solr escapes to be decoded
        escape_wildcards(bool): If Solr's wildcard indicators (* and ?)
            should be encoded (Default: False)
    returns:
        (str): same string after being decoded
    """
    if isinstance(value, str):
        value = Solr().decode_value(value, escape_wildcards)
    return value

@app.template_filter('set_child_key')
def set_child_key(parent_dict, parent_key, key, value):
    """Take dictionary of url components, and update 'key' with 'value'.
    args:
        parent_dict (dict): dictionary to add parent_key to
        parent_key (str|int|other hashable type): parent key to add to the parent_dict
        key (str|int|other hashable type): key to put under parent_key
        value (any): value to give that key
    returns:
        parent_dict (dict): The updated parent dictionary
    """
    if isinstance(parent_dict, dict) \
      and isinstance(parent_key, Hashable) \
      and isinstance(key, Hashable):
        if parent_key not in parent_dict:
            parent_dict[parent_key] = {}
        parent_dict[parent_key][key] = value
    return parent_dict

@app.template_filter('assemble_url')
def assemble_url(url_components):
    """Take url_components (derived from Flask Request object) and returns a url.
    args:
        url_components (dict): components of the URL to build
    returns:
        (str): fully combined URL with query arguments
    """
    url = ""
    if isinstance(url_components, dict) and "path" in url_components:
        url = url_components["path"]
        if "query_args" in url_components \
          and isinstance(url_components['query_args'], dict) \
          and url_components['query_args']:
            url = url + "?" + urllib.parse.urlencode(url_components["query_args"], doseq=True)
    return url

@app.template_filter('urlquote')
def urlquote(url_str):
    """Fully escapes all characters (including slash) in the given string with URL percent escapes
    args:
        url_str (str): The string to escape
    returns:
        (str): The fully escaped string
    """
    return urllib.parse.quote(url_str).replace('/', '%2F')

@app.template_filter('date_passed')
@catch((ValueError, TypeError),
       'Unable to get a valid date in "{value}". Error {exc}', return_val=False)
def date_passed(value):
    """ Checks if the embargoded date is greater than the current date
    args:
        value (str): Date in the format yyy-mm-dd that needs to be checked
    returns:
        (bool): If the given date is less than the current date or not
    """
    value_date = datetime.strptime(value, "%Y-%m-%d")
    current_date = datetime.now()
    return value_date.date() < current_date.date()

@app.template_filter('render')
@contextfilter
@catch(TemplateError, "Invalid template provided: {value}. Error: {exc}", return_val=None)
def render(context, value):
    """Renders a given string or literal
    args:
        context (Jinja2 context): context information and variables to use when
            evaluating the provided template string.
        value (str): Jinja2 template string to evaluate given the provided context
    returns:
        (str|None): the rendered value or string
    """
    data_template = context.environment.from_string(value)
    return data_template.render(**context)

@app.template_filter('render_literal')
@contextfilter
def render_literal(context, value, fallback_to_str=True):
    """Renders a Jinja template and attempts to perform a literal_eval on the result
    args:
        context (Jinja2 context): context information and variables to use when
            evaluating the provided template string.
        value (str): Jinja2 template string to evaluate given the provided context
        fallback_to_str (bool): If function should return string value on a failed
            attempt to literal_eval
    returns:
        (any|None) The literal_eval result, or string if fallback_to_str, or None on render failure
    raises:
        ValueError: If content is valid Python, but not a valid datatype
        SyntaxError: If content is not valid Python
    """
    context.environment.autoescape = False
    data_val = render(context, value)
    if data_val:
        try:
            data_val = literal_eval(data_val)
        except (ValueError, SyntaxError) as err:
            app.logger.debug(f"Could not literal eval {data_val}. Error: {err}")
            if not fallback_to_str:
                raise err
    context.environment.autoescape = True
    return data_val

@app.template_filter('format_date')
@catch((ValueError, TypeError), return_arg="default")
def format_date(value: str, default: str = "Indefinite") -> str:
    '''
    Format the provided embargo end date as a human readable string
    If there is no end date, it will show as 'Indefinite' (or the other
    default value prodived). It will only mark a valid date value as invalid
    if it is the year 9999.
    args:
        value (str): Embargo end date
    returns:
        (str): Formatted end date
    '''
    result = default

    value_date = datetime.strptime(value, "%Y-%m-%d")
    if value_date.year != 9999:
        suf = lambda n: "%d%s"%(n, {1:"st", 2:"nd", 3:"rd"}.get(n if n < 20 else n%10, "th"))
        result = value_date.strftime("%B %d %Y") # it is a valid date, so set that as the result
        day = value_date.strftime('%d')
        # Add in the suffix (st, th, rd, nd)
        result = result.replace(f" {day} ", f" {suf(int(day))}, ")

    return result

@app.template_filter('sandbug')
def sandbug_filter(value: str, comment: str = None):
    '''
    Writes debug statements to the sandhill log
    args:
        value (str): Message to write to the log
    '''
    sandbug(value, comment) # pylint: disable=undefined-variable
    return ""


@app.template_filter('deepcopy')
def deepcopy(obj):
    """
    Returns the deepcopy of the input object
    args:
        obj (dict, list, tuple): Any value which is not a scalar type.
    """
    return copy.deepcopy(obj)

@app.template_filter('getfilterqueries')
def getfilterqueries(query: dict):
    """
    Extracts the filter queries from the solr query
    args:
        query (dict): solr query
            (ex {"q":"frogs", "fq":["dc.title:example_title1", "dc.title:example_title2",
            "dc.creator:example_creator1", "dc.creator:example_creator2"]})
    return:
        (dict)
        (ex. {"dc.title": ["example_title1", "example_title2"], "dc.creator":
        ["example_creator1", "example_creator2"]})
    """
    def parse_fq_into_dict(fq_dict, fq_str):
        fq_pair = fq_str.split(":", 1)
        if not fq_pair[0] in fq_dict:
            fq_dict[fq_pair[0]] = []
        fq_dict[fq_pair[0]].append(solr_decode(fq_pair[1]))

    fqueries = {}
    if 'fq' in query:
        if isinstance(query['fq'], list):
            for fquery in query['fq']:
                parse_fq_into_dict(fqueries, fquery)
        else:
            parse_fq_into_dict(fqueries, query['fq'])
    return fqueries

@app.template_filter('addfilterquery')
def addfilterquery(query: dict, field: str, value: str):
    """
    Adds the field and value to the filter query.
    Also removes the 'start' query param if it exists under the
    assumption that a user removing facets would want to return
    to the first page.
    args:
        query (dict): solr query
            (ex: {"q": "frogs", "fq": "dc.title:example_title"})
        field (str): field that needs to be checked in the fliter query
            (ex: dc.creator)
        value (str): value that needs to be checked in the filter query
            (ex: example_creator)
    """
    if not 'fq' in query:
        query['fq'] = []

    if not isinstance(query['fq'], list):
        query['fq'] = [query['fq']]

    # TODO this only works when adding a fq value, but fails on an actual solr query
    fquery = ':'.join([field, solr_encode(value)])
    if fquery not in query['fq']:
        query['fq'].append(fquery)

    # removing the start query param when new filters are applied
    if 'start' in query:
        del query['start']

    return query

@app.template_filter('hasfilterquery')
def hasfilterquery(query: dict, field: str, value: str):
    """
    Ensure the filter query has the field and value
    args:
        query (dict): solr query
            (ex: {"q": "frogs", "fq": "dc.title:example_title"})
        field (str): field that needs to be checked in the fliter query
            (ex: dc.title)
        value (str): value that needs to be checked in the filter query
            (ex: example_title)
    """
    fqueries = [
        ':'.join([field, solr_encode(value)]),
        ':'.join([field, value])
    ]

    found = False
    if 'fq' in query:
        if not isinstance(query['fq'], list):
            if query['fq'] in fqueries:
                found = True
        else:
            for fquery in fqueries:
                if fquery in query['fq']:
                    found = True
    return found

@app.template_filter('removefilterquery')
def removefilterquery(query: dict, field: str, value: str):
    """
    Removes the filter query and returns the revised query.
    Also removes the 'start' query param if it exists under the
    assumption that a user removing facets would want to return
    to the first page.
    args:
        query (dict): solr query
            (ex: {"q": "frogs", "fq": "dc.title:example_title"})
        field (str): field that needs to be removed from the fliter query
            (ex: dc.title)
        value (str): value that needs to be removed from the filter query
            (ex: example_title)
    """
    fqueries = [
        ':'.join([field, solr_encode(value)]),
        ':'.join([field, value])
    ]

    if 'fq' in query:
        if not isinstance(query['fq'], list):
            if query['fq'] in fqueries:
                query['fq'] = []
        else:
            for fquery in fqueries:
                if fquery in query['fq']:
                    query['fq'].remove(fquery)

    # removing the start query param when new filters are applied
    if 'start' in query:
        del query['start']

    return query

@app.template_filter('maketuplelist')
def maketuplelist(input_list: list, tuple_length: int):
    """
    Convert a list into tuples of lenth tuple_length
    args:
        input_list (list): list with values that need to be converted into tuples
        tuple_length (int): length of tuples in the list
    """
    # if not evenly divisible by tuple_length excess values are discarded
    return list(zip(*[iter(input_list)]*tuple_length))

@app.template_filter('makedict')
def makedict(input_list: list):
    """
    Convert a list into a dictionary
    args:
        input_list (list): list with values that need to be converted into a dictionary
    """
    return dict(maketuplelist(input_list, 2))

@app.template_filter('regex_match')
@catch(re.error, "Regex error in regex_match. {exc}", return_val=None)
def regex_match(value, pattern):
    """
    Match pattern in the value
    args:
        value (str): value that the pattern will compare against
        pattern (str): regex patten that need to be checked
    """
    return re.match(pattern, value)

@app.template_filter('regex_sub')
@catch(TypeError, "Expected string in regex_sub. {exc}", return_arg='value')
@catch(re.error, "Invalid regex supplied to regex_sub. {exc}", return_arg='value')
def regex_sub(value, pattern, substitute):
    """
    Substitue pattern in the value
    args:
        value (str): value that need the substitution
        pattern (str): regex patten that need to be checked
        substitute (str): regex pattern that need to be substituted
    """
    return re.sub(pattern, substitute, value)

@app.template_filter('get_config')
def get_config_filter(name: str, default=None):
    """
    Get the value of the given config name. It will first
    check in the environment for the variable name, otherwise
    look in the app.config, otherwise use the default param
    args:
        name (str): Name of the config variable to look for
        default(str/None): The defaut value if not found elsewhere
    returns:
        (str): Value of the config variable, default value otherwise
    """
    return get_config(name, default)

@app.template_filter('commafy')
def commafy(value):
    '''
    Take a number and format with commas
    args:
        value(int): Integer value to comma format
    returns:
        ret(str): Comma-fied representation
    '''
    ret = ""

    if isinstance(value, int):
        ret = "{:,}".format(value)

    return ret

@app.template_filter('xpath')
def filter_xpath(value, xpath):
    '''
    Perform an XPath query against an XML source
    args:
        value(str): XML source
        xpath(str): An XPath query
    returns:
        (lxml Elements): A list of matching elements
    '''
    return xml.xpath(value, xpath)

@app.template_filter('xpath_by_id')
def filter_xpath_by_id(value, xpath):
    '''
    Perform an XPath query against an XML source and returns matched
    elements as a dict, where the key is the 'id' attribute of the
    element and the value is the XML content inside the element as a string.
    args:
        value(str): XML source
        xpath(str): An XPath query
    returns:
        (dict): A mapping of element 'id' to a string of XML for its children
    '''
    return xml.xpath_by_id(value, xpath)

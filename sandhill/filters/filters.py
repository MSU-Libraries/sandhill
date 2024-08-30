"""Filters for jinja templating engine"""
import urllib
import re
import html
import json
from typing import Any  # pylint: disable=unused-import
from collections.abc import Hashable
from datetime import datetime
import mimetypes
from ast import literal_eval
import copy
from dateutil import parser
from jinja2 import pass_context, TemplateError
from markupsafe import Markup
from sandhill import app, catch
from sandhill.utils.generic import getconfig, getdescendant
from sandhill.utils.solr import Solr
from sandhill.utils.html import HTMLTagFilter
from sandhill.utils import xml

@app.template_filter('formatbinary')
def formatbinary(value):
    """
    Format bytes size to JEDEC standard binary file size.\n
    Use: `4096 | formatbinary` = `"4 KB"` \n
    Args:
        value (str|int): Number of bytes. \n
    Returns:
        (str): The formatted bytesize or `0 B` on invalid input value. \n
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    nbytes = int(value) if f"{value}".isdigit() else 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024
        i += 1
    fsize = f'{nbytes:.1f}'.rstrip('0').rstrip('.')
    return f"{fsize} {suffixes[i]}"

@app.template_filter('islist')
def islist(value):
    """
    Check if given value is a list. \n
    Args:
        value (Any): The value to type check against. \n
    Returns:
        (bool): True if value is a list. \n
    """
    return isinstance(value, list)

@app.template_filter('getextension')
def getextension(value):
    """
    For a given mimetype, return the appropriate file extension.\n
    Use: `"image/jpeg" | getextension` = `"jpg"` \n
    Args:
        value (str): A mimetype string \n
    Returns:
        (str): The matching filetype extension (without leading `.`) or `???` not found. \n
    """
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
    """
    Returns the head of the list if value is a non-empty list, otherwise returns the orig value. \n
    Args:
        value (Any): Possible list from which to remove the first item from. \n
    Returns:
        (Any): The first item from the list, or the original value if it was not a list. \n
    """
    if isinstance(value, list) and value:
        value = value[0]
    return value

@app.template_filter('unescape')
def unescape(value):
    """
    Unescape special characters in a string of HTML.\n
    Use: `"Moon &amp; &#42;&#42;&#42;" | unescape` = `"Moon & ***"` \n
    Args:
        value (str): The string to unescape. \n
    Returns:
        (str): The unescaped string, or empty string if passed a non-string value. \n
    """
    return html.unescape(value) if isinstance(value, str) else ""

@app.template_filter('filtertags')
def filtertags(value, *args):
    """
    Filter out all HTML tags except for the ones specified \
    and marks the output as safe to render.\n
    Use: `<i><b>Hello</b></i> | filtertags('b')` = `<b>Hello</b>` \n
    Args:
        value (str): A string potentially containing HTML tags. \n
        *args (str): Tag names which are safe and will not be removed. \n
    Returns:
        (str): A string with tags removed (excluding those passed as *args). \n
               This string is marked `safe` and will not be further escaped by Jinja. \n
    """
    htf = HTMLTagFilter(tags=args)
    htf.feed(value)
    return Markup(htf.output)

@app.template_filter('solr_encodequery')
def solr_encodequery(query, escape_wildcards=False):
    """
    Parses and encode a Solr query arguments (the part after the colon). \n
    args:
        query (str): Solr query argument to encode. \n
        escape_wildcards (bool): If Solr's wildcard indicators (* and ?) \
                                 should be encoded (Default: False) \n
    returns:
        (str): The Solr query with appropriate characters encoded. \n
    """
    return Solr().encode_query(query, escape_wildcards=escape_wildcards)

@app.template_filter('solr_encode')
def solr_encode(value, escape_wildcards=False, preserve_quotes=False):
    """Filter to encode a value being passed to Solr \n
    Args:
        value (str): string to escape Solr characters \n
        escape_wildcards (bool): If Solr's wildcard indicators (* and ?) \
            should be encoded \n
            Default: `False` \n
        preserve_quotes (bool): If set to True, will prevent quotes on outside \
            of the string from being encoded \n
    Returns:
        (str): same string but with Solr characters encoded \n
    """
    quotes_exist = False

    if preserve_quotes and re.match('".*"', value):
        value = value.strip('"')
        quotes_exist = True

    if isinstance(value, str):
        value = Solr().encode_value(value, escape_wildcards)

    if quotes_exist:
        value = f"\"{value}\""

    return value

@app.template_filter('solr_decode')
def solr_decode(value, escape_wildcards=False):
    """Filter to decode a value previously encoded for Solr. \n
    Args:
        value (str): string with Solr escapes to be decoded \n
        escape_wildcards (bool): If Solr's wildcard indicators (* and ?) \
            should be encoded \n
            Default: `False` \n
    Returns:
        (str): same string after being decoded \n
    """
    if isinstance(value, str):
        value = Solr().decode_value(value, escape_wildcards)
    return value

@app.template_filter('setchildkey')
def setchildkey(parent_dict, parent_key, key, value):
    """
    Take dictionary of url components, and update 'key' with 'value'.\n
    Use: `{'a': {'x': '1'}} | setchildkey('a', 'y', '2')` = `{'a': {'x': '1', 'y': '2'}}` \n
    Args:
        parent_dict (dict): dictionary to add parent_key to \n
        parent_key (str|int|other hashable type): parent key to add to the parent_dict \n
        key (str|int|other hashable type): key to put under parent_key \n
        value (any): value to give that key \n
    Returns:
        parent_dict (dict): The updated parent dictionary \n
    """
    if isinstance(parent_dict, dict) \
      and isinstance(parent_key, Hashable) \
      and isinstance(key, Hashable):
        if parent_key not in parent_dict:
            parent_dict[parent_key] = {}
        parent_dict[parent_key][key] = value
    return parent_dict

@app.template_filter('assembleurl')
def assembleurl(urlcomponents):
    """
    Take urlcomponents (derived from Flask Request object) and returns a url. \n
    Args:
        urlcomponents (dict): components of the URL to build \n
    Returns:
        (str): fully combined URL with query arguments \n
    """
    url = ""
    if isinstance(urlcomponents, dict) and "path" in urlcomponents:
        url = urlcomponents["path"]
        if "query_args" in urlcomponents \
          and isinstance(urlcomponents['query_args'], dict) \
          and urlcomponents['query_args']:
            # Remove 'hidden' params
            for key in list(urlcomponents['query_args'].keys()):
                if key.startswith('_'):
                    del urlcomponents['query_args'][key]
            url = url + "?" + urllib.parse.urlencode(urlcomponents["query_args"], doseq=True)
    return url

@app.template_filter('urlquote')
def urlquote(url_str):
    """
    Fully escapes all characters (including slash) in the given string with URL percent escapes \n
    Args:
        url_str (str): The string to escape \n
    Returns:
        (str): The fully escaped string \n
    """
    return urllib.parse.quote(url_str).replace('/', '%2F')

@app.template_filter('datepassed')
@catch((ValueError, TypeError),
       'Unable to get a valid date in "{value}". Error {exc}', return_val=False)
def datepassed(value):
    """
    Checks if the embargoed date is greater than the current date \n
    Args:
        value (str): Date in the format yyy-mm-dd that needs to be checked \n
    Returns:
        (bool): If the given date is less than the current date or not \n
    """
    value_date = datetime.strptime(value, "%Y-%m-%d")
    current_date = datetime.now()
    return value_date.date() < current_date.date()

@app.template_filter('render')
@pass_context
@catch(TemplateError, "Invalid template provided: {value}. Error: {exc}", return_val=None)
@catch(TypeError, "Cannot render a non-string value: {value}. Error: {exc}", return_val=None)
def render(context, value, **kwargs):
    """Renders a given string using Jinja. \n
    Args:
        context (Jinja2 context): context information and variables to use when \
            evaluating the provided template string. Passed automatically. \n
        value (str): Jinja2 template string to evaluate given the provided context. \n
        **kwargs (dict): Additional key-value pairs to add to the render context. \n
    Returns:
        (str): the rendered string \n
    """
    if kwargs:
        kwargs.update(context)
        ctx = kwargs
    else:
        ctx = context

    data_template = context.environment.from_string(value)
    return data_template.render(**ctx)

@app.template_filter('renderliteral')
@pass_context
def renderliteral(context, value, fallback_to_str=True):
    """
    Renders string via Jinja and attempts to perform a literal_eval on the result. \n
    Args:
        context (Jinja2 context): context information and variables to use when \
            evaluating the provided template string. \n
        value (str): Jinja2 template string to evaluate given the provided context \n
        fallback_to_str (bool): If function should return string value on a failed \
            attempt to literal_eval \n
    Returns:
        (Any|None): The literal_eval result, or string if fallback_to_str, \
        or None on render failure \n
    Raises:
        ValueError: If content is valid Python, but not a valid datatype \n
        SyntaxError: If content is not valid Python \n
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

@app.template_filter('formatedate')
@catch((ValueError, TypeError), return_arg="default")
def formatedate(value, default="Indefinite"):
    '''
    Format the provided embargo end date as a human readable string. \n
    If the date year is 9999, it will show the default value. \n
    Args:
        value (str): A date string in the format YYYY-MM-DD \n
        default (str): The default string (Default: "Indefinite") \n
    Returns:
        (str): Formatted end date \n
    '''
    def day_suffix(dom):
        return {1:"st", 2:"nd", 3:"rd"}.get(dom if dom < 20 else dom%10, "th")

    result = default
    value_date = datetime.strptime(value, "%Y-%m-%d")
    if value_date.year != 9999:
        result = value_date.strftime("%B DAY %Y") # it is a valid date, so set that as the result
        # Add in the suffix (st, th, rd, nd)
        result = result.replace("DAY", f"{value_date.day}{day_suffix(value_date.day)},")
    return result

@app.template_filter('formatiso8601')
@catch((ValueError, TypeError), return_arg="default")
def formatiso8601(value, dtfmt="%Y-%m-%d", default="Any"):  # pylint: disable=unused-argument
    '''
    Format the provided ISO 8601 date string. \n
    Args:
        value (str): A date string in the ISO 8601 format \n
        dtfmt (str): The format string to output (see `datetime.strftime`) \n
        default (str): The default string (Default: "Any") \n
    Returns:
        (str): Formatted date string \n
    '''
    value_date = parser.isoparse(value)
    return value_date.strftime(dtfmt)

@app.template_filter('sandbug')
def filter_sandbug(value: str, comment: str = None):
    '''
    Writes a variable to the Sandhill debug logs. \n
    Args:
        value (str): Variable to write to the log. \n
        comment (str|None): Optional comment to add to the log. \n
    Returns:
        (str): Always returns an empty string. \n
    '''
    sandbug(value, comment) # pylint: disable=undefined-variable
    return ""


@app.template_filter('deepcopy')
def deepcopy(obj):
    """
    Returns the deepcopy of the input object. \n
    Args:
        obj (dict|list|tuple): The value to deepcopy. \n
    Returns:
        (dict|list|tuple): The new copy of the variable. \n
    """
    return copy.deepcopy(obj)

@app.template_filter('solr_getfq')
def solr_getfq(query: dict):
    """
    Extract and returns the filter queries from a Solr query.\n
    Example input: \n
    ```
    {"q":"frogs", "fq":["dc.title:example_title1", "dc.title:example_title2",
    "dc.creator:example_creator1", "dc.creator:example_creator2"]}
    ``` \n
    Example output: \n
    ```
    {"dc.title": ["example_title1", "example_title2"], "dc.creator":
    ["example_creator1", "example_creator2"]}
    ``` \n
    Args:
        query (dict): A Solr query. \n
    Returns:
        (dict): The extracted filter queries. \n
    """
    def parse_fq_into_dict(fq_dict, fq_str):
        fq_pair = fq_str.split(":", 1)
        if len(fq_pair) != 2:
            app.logger.debug(f"Could not split invalid Solr fq: {fq_str}")
            return
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

@app.template_filter('solr_addfq')
def solr_addfq(query: dict, field: str, value: str):
    """
    Adds the field and value to the filter query.\n
    Also removes the `start` query param if it exists under the
    assumption that a user removing facets would want to return
    to the first page.
    Args:
        query (dict): Solr query (e.g. `{"q": "frogs", "fq": "dc.title:example_title"}`)
        field (str): field that needs to be checked in the filter query (e.g. `dc.creator`)
        value (str): value that needs to be checked in the filter query (e.g. `example_creator`)
    Returns:
        (dict): The updated query dict
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

@app.template_filter('solr_facetdates')
def solr_facetdates(filters: list, parameter: str):
    """
    In the provided list, look for the parameter starting by the parameter value,
     and extract the year range
    Args:
        filters (list): A list to loop through
        parameter (str): The start of the parameter we want (ie: "parameter" => "parameter=123")
    Returns:
        (dict): A dictionary containing the index "min" and "max", with the year of the range in it
    """
    facet_min_year = None
    facet_max_year = None
    value = findstartswith(filters, parameter)
    if value:
        solr_range = solr_extractrange(value)
        if solr_range:
            facet_min_year = formatiso8601(solr_range[0], '%Y')
            facet_max_year = formatiso8601(solr_range[1], '%Y')

    return {
        "min": facet_min_year,
        "max": facet_max_year,
    }

@app.template_filter('solr_extractrange')
def solr_extractrange(value: str):
    """
    Given a string, if a range in the format [START TO END] is present,
     it will extract and return both in a tuple
    Args:
        value (str): The string to look into
    Returns:
        (Tuple|None): A Tuple containing the 2 end of the range, if matching
    """
    result = re.search(r'\[(\S+) TO (\S+)\]', value)
    return result.groups() if result else None

@app.template_filter('findstartswith')
def findstartswith(filters: list, item: str):
    """
    Given a list, return the first element starting with the string item
    Args:
        filters (list): A list to loop through
        item (str): The start of the string we want (ie: "parameter" => "parameter=123")
    Returns:
        (str|None): The value in the list, if matching
    """
    for value in filters:
        if value.startswith(item) :
            return value
    return None

@app.template_filter('solr_hasfq')
def solr_hasfq(query: dict, field: str, value: str):
    """
    Check if filter query has the given field and value.
    Args:
        query (dict): Solr query (e.g. `{"q": "frogs", "fq": "dc.title:example_title"}`)
        field (str): field that needs to be checked in the filter query (e.g. `dc.title`)
        value (str): value that needs to be checked in the filter query (e.g. `example_title`)
    Returns:
        (bool): True if the filter query was found.
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

@app.template_filter('solr_removefq')
def solr_removefq(query: dict, field: str, value: str):
    """
    Removes the filter query and returns the revised query.
    Also removes the 'start' query param if it exists under the
    assumption that a user removing facets would want to return
    to the first page.
    Args:
        query (dict): Solr query (e.g. `{"q": "frogs", "fq": "dc.title:example_title"}`)
        field (str): field that needs to be removed from the filter query (e.g. `dc.title`)
        value (str): value that needs to be removed from the filter query (e.g. `example_title`)
    Returns:
        (dict): The updated query dict
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

@app.template_filter('totuples')
def totuples(input_list: list, tuple_length: int):
    """
    Convert a list into tuples of length tuple_length
    Args:
        input_list (list): list with values to be converted into tuples
        tuple_length (int): length of tuples in the list
    Returns:
        (list): A list of tuples
    """
    # if not evenly divisible by tuple_length excess values are discarded
    return list(zip(*[iter(input_list)]*tuple_length))

@app.template_filter('todict')
def todict(input_list: list):
    """
    Convert a list into a dictionary, alternating key and value to create pairs.
    Args:
        input_list (list): list with values to be converted into a dictionary
    Returns:
        (dict): The new dictionary
    """
    return dict(totuples(input_list, 2))

@app.template_filter('regex_match')
@catch(re.error, "Regex error in regex_match. {exc}", return_val=None)
def regex_match(value, pattern):
    """
    Match the pattern in the value.
    Args:
        value (str): value that the pattern will compare against
        pattern (str): regex pattern that need to be checked
    Returns:
        The regular expression match, as returned by `re.match()`
    """
    return re.match(pattern, value)

@app.template_filter('regex_sub')
@catch(TypeError, "Expected string in regex_sub. {exc}", return_arg='value')
@catch(re.error, "Invalid regex supplied to regex_sub. {exc}", return_arg='value')
def regex_sub(value, pattern, substitute):
    """
    Substitute a pattern in the value.
    Args:
        value (str): value that need the substitution
        pattern (str): regex pattern that need to be checked
        substitute (str): regex pattern that need to be substituted
    Returns:
        (str): The value with patterns substituted
    """
    return re.sub(pattern, substitute, value)

@app.template_filter('getconfig')
def filter_getconfig(name: str, default=None):
    """
    Get the value of the given config name. It will first
    check in the environment for the variable name, otherwise
    look in the app.config, otherwise use the default param
    Args:
        name (str): Name of the config variable to look for
        default (str): The defaut value if not found elsewhere
    Returns:
        (str): Value of the config variable, default value otherwise
    """
    return getconfig(name, default)

@app.template_filter('commafy')
def commafy(value):
    '''
    Take a number and format with commas.\n
    Use: `1234567 | commafy` = `"1,234,567"`
    Args:
        value (int): Integer value to comma format
    Returns:
        (str): Comma-fied representation
    '''
    ret = ""
    if isinstance(value, int):
        ret = f"{value:,}"
    return ret

@app.template_filter('xpath')
def filter_xpath(value, xpath):
    '''
    Perform an XPath query against an XML source
    Args:
        value (str): XML source
        xpath (str): An XPath query
    Returns:
        (list): A list of matching lxml.etree._Elements
    '''
    return xml.xpath(value, xpath)

@app.template_filter('xpath_by_id')
def filter_xpath_by_id(value, xpath):
    '''
    Perform an XPath query against an XML source and returns matched
    elements as a dict, where the key is the 'id' attribute of the
    element and the value is the XML content inside the element as a string.
    Args:
        value (str): XML source
        xpath (str): An XPath query
    Returns:
        (dict): A mapping of element 'id' to a string of XML for its children
    '''
    return xml.xpath_by_id(value, xpath)

@app.template_filter('json_embedstring')
def json_embedstring(value):
    '''
    Escape a string for embedding inside a JSON string. Does nothing
    for non-string values.
    Args:
        value (string): The string
    Returns:
        (string): The input escaped for embedding inside a JSON string
    '''
    if not isinstance(value, str):
        return value
    encoded = json.JSONEncoder().encode(value)
    # Replace outer quotes with escaped quotes
    #encoded = r'\"' + encoded[1:-1] + r'\"'
    encoded = encoded[1:-1]
    return encoded

@app.template_filter('getdescendant')
def filter_getdescendant(obj, list_keys, default=None):
    '''
    Gets key values from the dictionary/list if they exist;
    will check recursively through the `obj`.
    Args:
        obj (dict|list): A dict/list to check, possibly containing nested dicts/lists.
        list_keys (list|str): List of descendants to follow (or . delimited string)
        default (Any): Default value to return if no match found. Default of None.
    Returns:
        (Any): The last matching value from list_keys, or default value if not match found.
    '''
    found = getdescendant(obj, list_keys)
    return default if found is None else found

@app.template_filter('indexvaluegreaterthan')
def filter_indexvaluegreaterthan(tuples: list, index, value: int = None):
    '''
    Loop through a list of tuples,
    if the value at index is greater than value return the current tuple
    Args:
        tuples (list[tuple]): A list of tuples
        index (int): Index of the tuple to compare the value to
        value (int): (Default 1) Limit value to be greater than
    Returns:
        (tuple): All the tuple with the value at index greater than value.
    '''
    if not isinstance(value, (int, str)):
        value = 1
    value = int(value)
    for tup in tuples:
        if tup[index] > value:
            yield tup

@app.template_filter('pluralizer')
def filter_pluralizer(term: str, number: int):
    '''
    If count is greater than 1, add an s to the string.
    Args:
        term (str): A string to switch to plural if needed.
        number (int): Number to compare against to check if plural is needed.
    Returns:
        (str|Any): The term in plural form or not; if parameters are not properly casted, return the term parameter unchanged
    '''
    if isinstance(term, str) and isinstance(number, int) and number > 1:
        return term + 's'
    else:
        return term

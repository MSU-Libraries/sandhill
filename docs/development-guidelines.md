Code Standards
==============
Here are the general guidelines for development in core Sandhill. You may wish to
keep to these when developing your own instance code as well. If you plan on
contributing code back to Sandhill, sticking to these guidelines will make the
process much easier on us!

File Naming
-----------------------
Python file names are to be in all lower case, and where required, will use an underscore (`_`) to
separate words.

Imports
-------
Import statements are to include the full path instead of a relative path.
```
from sandhill.processors import my_processor
```

Code Design
----------------
Sandhill developers use `pylint` to verify syntax structure of all our code.
The settings used are avalable in `.pylintrc` and you can run `pylint` on your
Sandhill instance with the included `run-pylint` shell script.

These are not hard requirements, but developers should strive to stay within the
limitations raised by pylint if at all possible.

Code Style
-----------
In general, we will be following [PEP 8](https://www.python.org/dev/peps/pep-0008) for code styling.
Note that not all of these standards will not be captured through linting. 

For a quick reference see [this grid](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#3164-guidelines-derived-from-guidos-recommendations).

Docstrings Style
--------------
In general, we will be using the [Google docstring style](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings). 

One addition to these standards is to include the data type for all arguments and 
return values. For example:

```python
def getdescendant(obj, list_keys, extract=False, put=None):
    """
    Gets key values from the dictionary/list if they exist;
    will check recursively through the `obj`.
    Args:
        obj (dict|list): A dict/list to check, possibly containing nested dicts/lists.
        list_keys (list|str): List of descendants to follow (or . delimited string)
        extract (bool): If set to true, will remove the last matching value from the `obj`.
        put (Any): Replace the found value with this new value in the `obj`,
                   or append if the found value at a list key of `"[]"`
    Returns:
        (Any): The last matching value from list_keys, or None if no match
    """
    ...
```

Naming Conventions
----------------
### Files
* Files should be named based on context rather than action(s) it may perform.
  * E.g. A `commands/scss.py` with a `--compile` flag is preferred over `commands/compile_scss.py`
* The context should not be overly broad.

### Functions/Methods
* Function names should attempt to prefer shorter names when possible.
* Grammatically, function names should attempt one of the following structures:
  * `verb()`
  * `noun()`
  * `verb_noun()`
* When additional context is appropriate, add a prefix to the function to indicate it:
  * `context_verb()`
  * `context_noun()`
  * `context_verb_noun()`
* Functions should avoid specifying input types as part of the function name. Use documentation and type hinting instead.
  * E.g. `to_widget()` is preferred over `convert_list_into_widget()`
* Jinja filters and context processor should avoid understores:
  * E.g. `setchildkey` is preferred to `set_child_key`

### Function/Method Parameters
* Parameters should indicate what is to be passed rather than imply it.
  * E.g. For a function accepting allowed tags, `tags` is preferred over `allow`. If multiple tag params would be accepted, then differentiate them like `tags_allowed` or `allowed_tags`.
* Boolean flags to function are discouraged, but it is understood they may be sometimes necessary.
  * The number of boolean flags to functions should be minimal.
  * Boolean flags should be keyword arguments only. This can be accomplished by disabling positional arguments using the `*` parameter.
    * E.g. `myfunc(param1, param2, *, myflag=False)` would require that `myflag` always be passed as a keyword argument


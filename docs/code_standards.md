Code Standards
==============

File Naming Conventions
-----------------------
File names will be in all lower case, and where required, will use an underscore (`_`) to 
separate words.

Imports
-------
Import statements will include the full path instead of a relative path.
```
from sandhill.processors import my_processor
```

Function Length
----------------
Generally speaking, functions should not be more than 40 statements of code. 
This is used instead of lines of code so it will not count comment blocks 
or multi-line statements. 

Code Style
-----------
In general, we will be following [PEP 8](https://www.python.org/dev/peps/pep-0008) for code styling.
Note that not all of these standards will not be captured through linting. 

As a quick summary, we can reference [this grid](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#3164-guidelines-derived-from-guidos-recommendations): 

<table rules="all" border="1" summary="Guidelines from Guido's Recommendations"
       cellspacing="2" cellpadding="2">

  <tr>
    <th>Type</th>
    <th>Public</th>
    <th>Internal</th>
  </tr>

  <tr>
    <td>Packages</td>
    <td><code>lower_with_under</code></td>
    <td></td>
  </tr>

  <tr>
    <td>Modules</td>
    <td><code>lower_with_under</code></td>
    <td><code>_lower_with_under</code></td>
  </tr>

  <tr>
    <td>Classes</td>
    <td><code>CapWords</code></td>
    <td><code>_CapWords</code></td>
  </tr>

  <tr>
    <td>Exceptions</td>
    <td><code>CapWords</code></td>
    <td></td>
  </tr>

  <tr>
    <td>Functions</td>
    <td><code>lower_with_under()</code></td>
    <td><code>_lower_with_under()</code></td>
  </tr>

  <tr>
    <td>Global/Class Constants</td>
    <td><code>CAPS_WITH_UNDER</code></td>
    <td><code>_CAPS_WITH_UNDER</code></td>
  </tr>

  <tr>
    <td>Global/Class Variables</td>
    <td><code>lower_with_under</code></td>
    <td><code>_lower_with_under</code></td>
  </tr>

  <tr>
    <td>Instance Variables</td>
    <td><code>lower_with_under</code></td>
    <td><code>_lower_with_under</code> (protected)</td>
  </tr>

  <tr>
    <td>Method Names</td>
    <td><code>lower_with_under()</code></td>
    <td><code>_lower_with_under()</code> (protected)</td>
  </tr>

  <tr>
    <td>Function/Method Parameters</td>
    <td><code>lower_with_under</code></td>
    <td></td>
  </tr>

  <tr>
    <td>Local Variables</td>
    <td><code>lower_with_under</code></td>
    <td></td>
  </tr>

</table>


Comments Style
--------------
In general, we will be using the [Google docstring style](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings). 

Here are some examples for quick reference.

Our addition to these standards is to include the data type for all arguments and 
return values.

### Function
```
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
        table_handle (Table): An open smalltable.Table instance.
        keys (List of string): A sequence of strings representing the key of each table
          row to fetch.  String keys will be UTF-8 encoded.
        require_all_keys (bool): Optional; If require_all_keys is True only
          rows with values set for all keys will be returned.

    Returns (dict):
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings. For
        example:

        {b'Serak': ('Rigel VII', 'Preparer'),
         b'Zim': ('Irk', 'Invader'),
         b'Lrrr': ('Omicron Persei 8', 'Emperor')}

        Returned keys are always bytes.  If a key from the keys argument is
        missing from the dictionary, then that row was not found in the
        table (and require_all_keys must have been False).

    Raises:
        IOError: An error occurred accessing the smalltable.
    """
```

### Class
```
    """Summary of class here.

    Longer class information....
    Longer class information....

    Attributes:
        likes_spam (bool): A boolean indicating if we like SPAM or not.
        eggs (int): An integer count of the eggs we have laid.
    """
```

### Block and Inline Comments:
```
# We use a weighted dictionary search to find out where i is in
# the array.  We extrapolate position based on the largest num
# in the array and the array size and then do binary search to
# get the exact number.

if i & (i-1) == 0:  # True if i is 0 or a power of 2.
```

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

Code Style
-----------
In general, we will be following [PEP 8](https://www.python.org/dev/peps/pep-0008) for code styling. 

Here are some examples for quick reference of variable names.

### Global Variables
All capital letters with an underscore between words:
```
GLOBAL_VAR
```

### Class Names
Titlecase without spaces between words: 
```
MyClass
```

Comments Style
--------------
In general, we will be using the [Google docstring style](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings). 

Here are some examples for quick reference.

### Function
```
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
        table_handle: An open smalltable.Table instance.
        keys: A sequence of strings representing the key of each table
          row to fetch.  String keys will be UTF-8 encoded.
        require_all_keys: Optional; If require_all_keys is True only
          rows with values set for all keys will be returned.

    Returns:
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
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
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

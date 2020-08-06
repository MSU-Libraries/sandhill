Metadata Configuration
---------------
This document describes how to manage the metadata display, downloads section and restrictions on 
item pages within Sandhill.

Define the Configuration File
============================================
Files must be named after the namespace (ex: `etd.json`) or 
based on the type (ex: `pdf.json`). 


Field Definitions
================
Sample configuration:  
```
{
    "match_conditions": [
        {
            "value": "{{ view_args.namespace }}",
            "allowed": ["etd"]
        },
        {
            "value": "{{ item['RELS_EXT_info:fedora/fedora-system:def/model#hasModel_uri_s'] }}",
            "allowed": ["info:fedora/islandora:sp_pdf"]
        }
    ],
    "title_field": "fgs_label_s",
    "media_template": "media_display/preview.html.j2",
    "restriction_conditions": [
        {
            "value": "{{ item.embargo_end_date_ss | head | date_passed if item.embargo_end_date_ss is defined else False }}",
            "allowed": ["True"]
        }
    ],
    "display": [
        {
            "field": "description",
            "label": "Abstract",
            "metadata_template": "item_page_blocks/metadata_expand_block.html.j2"
        },
        {
            "field": "collection_t",
            "label": "In Collections",
            "metadata_template": "item_page_blocks/metadata_descriptive_list.html.j2",
            "link": "/{{ view_args.namespace }}"
        }
    ],
    "downloads": [
        {
            "label": "Original file",
            "mime_type_field": "fedora_datastream_latest_OBJ_MIMETYPE_ms",
            "file_size_field": "fedora_datastream_latest_OBJ_SIZE_ms",
            "datastream": "OBJ",
            "restricted": true
        },
        {
            "label": "Low-resolution image",
            "mime_type_field": "fedora_datastream_latest_PREVIEW_MIMETYPE_ms",
            "file_size_field": "fedora_datastream_latest_PREVIEW_SIZE_ms",
            "datastream": "PREVIEW"
        }
    ]
}

```

### Match Conditions


`match_conditions` will determinte the route for the path.
A route must match all the conditions in the config file, 
if not, an error page with a "not implemented"(501) is returned to the user.

`match_conditions` is a list of dicts.

Example:
```
    "match_conditions": [
        {
            "value": "{{ view_args.namespace }}",
            "allowed": ["etd"]
        },
        {
            "value": "{{ item['RELS_EXT_info:fedora/fedora-system:def/model#hasModel_uri_s'] }}",
            "allowed": ["info:fedora/islandora:sp_pdf"]
        }
    ],
```
* `value`: Value to compare. The item data from solr is availabe in a varibale `item`, which can be used to compute the value.
* `allowed`: List of acceptable values, these values are compared with the provided value to determine a match



### Restriction Conditions

`restriction_conditions` can be added to the config files, 
which determines if any restrictions can be applied to the item.

`restriction_conditions` is a list of dicts.

Example:
```
    "restriction_conditions": [
        {
            "value": "{{ item.embargo_end_date_ss | head | date_passed if item.embargo_end_date_ss is defined else False }}",
            "allowed": ["True"]
        }
    ],
```
* `value`: Value to compare. Can use jinja2 variables and filters to determine the value. 
The item data from solr is availabe in a varibale `item`, which can be used to compute the value.
* `allowed`: List of acceptable values, these values are compared with the provided value to determine a match.


### General Fields
* `title_field`: The Solr field to use for the title on the item page
* `media_template`: The template file within the `sandhill\templates` directory to use for the object viewer

### Display Fields  
These configurations are used to render the downloads section on the page
* `field`: Solr field to display the value of
* `label`: The label to use for the field
* `metadata_template`: The template file within the `sandhill\templates` directory to display this field
* (Optional) `link`: If provided, will turn the metadata value into a link. Jinja varibales and filters can be used in the field.
for more information

### Downloads Fields
These configurations are used to render the downloads section on the page

* `label`: The label to use for the object in the downloads section.
* `mime_type_field`: Mimetype of the object in the downloads section.
* `file_size_field`: Filesize of the object.
* `datastream`: Fedora datastream of the object. This is used to generate the "view" and "download" links.
* (Optional) `restricted`: If provided and set to true, the object will not be displayed in the downloads box given that the restriction conditions are met. 
See [Restriction Conditions](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/tree/development/instance%2Fmetadata_configs#Restriction%20Conditions)
for more information



Variables
============

### Special Variables
* `link` field within the `display` section has the ability to create dynamic URLs with variables 
used through out the page. Some examples of variables available are: 
* `metadata_value` which is the value of the current metadata field
* `view_args.namespace` and `view_args.id` come from the route configs in the `routes` section and 
* `item` is the solr response for the record. It is a dictinoary with solr fields as keys and their corresponding values. 
represent the pid components

Additionally, you can dynamically alter the values of the variables used by using Jinja2 filters. To add 
to the existing Jinja2 filters, there are custom ones available within our [filters](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/blob/master/sandhill/utils/filters.py) file. Some examples are: 
* `solr_escape`: A custom filter, which will take a alue and escape the special Solr characters
* `urlencode`: Encode the value to be used in a URL



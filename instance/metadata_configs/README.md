Metadata Configuration
---------------
This document describes how to manage the metadata display, downloads section and restrictions on 
item pages within Sandhill.

Define the Configuration File
============================================
From Sandhill's perspective, config files can be named arbitrarily. 
One particular naming system that might be logical to employ would use namespace (ex: `etd.json`) or type (ex: `pdf.json`). 

In addition to more familiar data types, such as strings and integers, all [jinja template functionality](https://jinja.palletsprojects.com/en/2.11.x/templates/) is
available to be included in the values specified in each metadata configuration file. For instance,
`{{ view_args.namespace }}` is a jinja expression that will be evaluated internally to arrive at the actual value to be
included on the page.

Field Definitions
================
Sample configuration:  
```
{
    "match_conditions": [
        {
            "value": "{{ view_args.namespace }}",
            "allowed": ["etd", "austm"]
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
        },
        {
            "field": "name_thesis_advisor",
            "label": "Thesis Advisors",
            "metadata_template": "item_page_blocks/metadata_descriptive_list.html.j2",
            "link": "/search?fq=name_thesis_advisor:{{ metadata_value | solr_escape | urlencode  }}"
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


`match_conditions` will determine the route for the path.
A route must match all the conditions in the config file. 
If not, an error page with a "501 Not Implemented" error is returned to the user.

`match_conditions` is a list of python dictionaries.

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
    ]
```
* `value`: This is the value in the current context to be compared to allowed values. This string is rendered through jinja before comparison.
* `allowed`: List of acceptable values, these values are compared with the provided `value` to determine a match. Matches must be exact.



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
    ]
```
* `value`: This is the value in the current context to be compared to allowed values. This string is rendered through jinja before comparison.
* `allowed`: List of acceptable values, these values are compared with the provided value to determine a match. Matches must be exact.


### General Fields
* `title_field`: The Solr field to use for the title on the item page
* `media_template`: The template file within the `sandhill\templates\media_display` directory to use for the object viewer

### Display Fields  
These configurations are used to render the downloads section on the page
* `field`: Solr field to display the value. 
* `label`: The label to use for the field.
* `metadata_template`: The template file within the `sandhill\templates\item_page_blocks` directory to display this field
* (Optional) `link`: If provided, will turn the metadata value into a link. The string is rendered through jinja.

### Downloads Fields
These configurations are used to render the downloads section on the page

* `label`: The label to use for the object in the downloads section.
* `mime_type_field`: Mimetype of the object in the downloads section.
* `file_size_field`: Filesize of the object.
* `datastream`: Fedora datastream of the object. This is used to generate the "view" and "download" links.
* (Optional) `restricted`: If provided and set to true, the object will not be displayed in the downloads box given that the restriction conditions are met. 
See [Restriction Conditions](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/blob/itempage/instance/metadata_configs/README.md#restriction-conditions)
for more information



Variables
============
* `link` field within the `display` section has the ability to create dynamic URLs with variables.
* `restricted` field within the `downloads` section can be used to control the display of the downloads object based on the restriction conditions. 
See [Restriction Conditions](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/blob/itempage/instance/metadata_configs/README.md#restriction-conditions) for more information. 

### Jinja2 Variables
All variables defined in template files are available to be used in configuration files.
* `metadata_value` is a variable that is available in the templates 
Example display field:
```
{
    "field": "name_thesis_advisor",
    "label": "Thesis Advisors",
    "metadata_template": "item_page_blocks/metadata_descriptive_list.html.j2",
    "link": "/search?fq=name_thesis_advisor:{{ metadata_value | solr_escape | urlencode  }}"
}

```
Example template:
```
<dl class="row my-sm-3 sandhill_metadata_descriptive_list">
    <dt class="col-sm-3" id="sandhill_metadata_field">{{ display_conf['label']  }}</dt>
    <dd class="col-sm-9" aria-labelledby="sandhill_metadata_field">
        {% if item[display_conf['field']] | is_list %}
            {% for  metadata_value in  item[display_conf['field']] %}
                {% include 'item_page_blocks/display_field.html.j2' %}
                <br/>
            {% endfor %}
        {% else %}
            {% set metadata_value = item[display_conf['field']] %}
            {% include 'item_page_blocks/display_field.html.j2' %}
        {% endif %}
    </dd>
</dl>
```
* `view_args.namespace` and `view_args.id`  are set in the route configs in the `routes` section and 
represent the pid components
Example route config:
```
{
    "route": [
        "/<string:namespace>/<int:id>",
        "/<string:namespace>:<int:id>"
    ],
    "template": "item.html.j2",
    "data": [
        {
            "name": "item",
            "processor": "solr.query_record",
            "on_fail": 404,
            "params": {
                "q": "PID:\"{{ view_args.namespace }}:{{ view_args.id }}\"",
                "wt": "json"
            }
        },
        {
            "name": "metadata_conf",
            "processor": "file.load_matched_json",
            "on_fail": 501
        },
        {
            "name": "restriction",
            "processor": "evaluate.conditions",
            "on_fail": 401,
            "conditions": "metadata_conf.restriction_conditions"
        }
    ]
}

```
* `item` is the solr response for the record. It is a dictionary with solr fields as keys and their corresponding values.
The variable is set in the route configs in the `data` section.


Additionally, you can dynamically alter the values of the variables used by using Jinja2 filters. To add 
to the existing Jinja2 filters, there are custom ones available within our [filters](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/blob/master/sandhill/utils/filters.py) file. Some examples are: 
* `solr_escape`: A custom filter, which will take a alue and escape the special Solr characters
* `urlencode`: Encode the value to be used in a URL



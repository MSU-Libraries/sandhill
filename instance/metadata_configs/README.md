Metadata Configuration
---------------
This document describes how to manage the metadata display, downloads section and restrictions on 
item pages within Sandhill.

Define the Configuration File
============================================
From Sandhill's perspective, config files can be named arbitrarily. 
One particular naming system that might be logical to employ would use namespace (ex: `etd.json`) or type (ex: `pdf.json`). 

In addition to more familiar data types, such as strings and integers, all [Jinja template functionality](https://jinja.palletsprojects.com/en/2.11.x/templates/) is
available to be included in the values specified in each metadata configuration file. For instance,
`{{ view_args.namespace }}` is a Jinja expression that will be evaluated internally to arrive at the actual value to be
included on the page.

Field Definitions
================
### Sample configuration  
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
    "title": "{{ item. fgs_label_s }}",
    "media_template": "media_display/preview.html.j2",
    "restriction_conditions": [
        {
            "value": "{{ item.embargo_end_date_ss | head | date_passed if item.embargo_end_date_ss is defined else True }}",
            "allowed": ["False"]
        }
    ],
    "display": [
        {
            "value": "{{ item.description }}",
            "label": "Abstract",
            "metadata_template": "item_page_blocks/metadata_expand_block.html.j2"
        },
        {
            "value": "{{ item.collection_t }}",
            "label": "In Collections",
            "metadata_template": "item_page_blocks/metadata_descriptive_list.html.j2",
            "link": "/{{ view_args.namespace }}"
        },
        {
            "value": "{{ item.name_thesis_advisor }}",
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
* `value`: This is the value in the current context to be compared to allowed values. This string is rendered through Jinja before comparison.
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
* `value`: This is the value in the current context to be compared to allowed values. This string is rendered through Jinja before comparison.
* `allowed`: List of acceptable values, these values are compared with the provided value to determine a match. Matches must be exact.


### General Fields
* `title`: The Solr field to use for the title on the item page
* `media_template`: The template file within the `sandhill\templates\media_display` directory to use for the object viewer

### Display Fields  
These configurations are used to render the metadata section on the page. 

* `value`: Value of the field, which can use the Solr field. 
* `label`: The label to use for the field.
* `metadata_template`: The template file within the `sandhill\templates\item_page_blocks` directory to display this field.
    
    Available metadata templates
    * `item_page_blocks/metadata_expand_block.html.j2`: A template that creates a toggle for the visibility of content.
    * `item_page_blocks/metadata_descriptive_list.html.j2`: A template that creates a descriptive list of fields and values.
* (Optional) `link`: If provided, will turn the metadata value into a link. The string is rendered through Jinja.

Example display field:
```
{
    "value": "{{ item.name_thesis_advisor }}",
    "label": "Thesis Advisors",
    "metadata_template": "item_page_blocks/metadata_descriptive_list.html.j2",
    "link": "/search?fq=name_thesis_advisor:{{ metadata_value | solr_escape | urlencode  }}"
}
```

All variables defined in the route config and in template files are available to be used in configuration files.
For example, in the above `link` value, `metadata_value` is referring to the `metadata_value` defined in the template file - see example below. 

Example contents of `metadata_template` file:
```
<dl class="row my-sm-3 sandhill_metadata_descriptive_list">
    <dt class="col-sm-3" id="sandhill_metadata_field">{{ display_conf['label']  }}</dt>
    <dd class="col-sm-9" aria-labelledby="sandhill_metadata_field">
        {% if display_conf['value'] | is_list %}
            {% for  metadata_value in  display_conf['value'] %}
                {% include 'item_page_blocks/display_field.html.j2' %}
                <br/>
            {% endfor %}
        {% else %}
            {% set metadata_value = display_conf['value'] %}
            {% include 'item_page_blocks/display_field.html.j2' %}
        {% endif %}
    </dd>
</dl>
```

### Downloads Fields
These configurations are used to render the downloads section on the page.

* `label`: The label to use for the object in the downloads section.
* `mime_type_field`: Mimetype of the object in the downloads section.
* `file_size_field`: Filesize of the object.
* `datastream`: Fedora datastream of the object. This is used to generate the "view" and "download" links.
* (Optional) `restricted`: If provided and set to true, the object will not be displayed in the downloads box given that the restriction conditions are met. 
See [Restriction Conditions](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/blob/itempage/instance/metadata_configs/README.md#restriction-conditions)
for more information

Example `downloads` field:
```
{
    "label": "Original file",
    "mime_type_field": "fedora_datastream_latest_OBJ_MIMETYPE_ms",
    "file_size_field": "fedora_datastream_latest_OBJ_SIZE_ms",
    "datastream": "OBJ",
    "restricted": true
}
```

Route Config Variables
=======================

### Jinja2 Variables
* `view_args.namespace` and `view_args.id`  are set in the route configs in the `routes` section and 
represent the pid components

### Route config explanation
The route has a list of `data` sources; each `data` entry has a `name`. The value of the `name` is the name of the variable. 

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
            "conditions": "metadata_conf.restriction_conditions",
            "match_all": true
        }
    ]
}

```

For example, this is the route config for the `item.html.j2` template. 
In the `data` section, `name` has a value of `item`. `item` will be available inside that template, and will contain the results of the `solr.query_record` data processor. 
See the example at the top of the page, in the Field Definitions section, under ["Sample Configuration"](#sample-configuration) > `match_conditions`. 
Look for the second set of curly braces, at the line that starts with `value`. 

* `item` is the Solr response for the record. It is a dictionary with solr fields as keys and their corresponding values.
The variable is set in the route configs in the `data` section.


Additionally, you can dynamically alter the values of the variables used by using Jinja2 filters. To add 
to the existing Jinja2 filters, there are custom ones available within our [filters](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/blob/master/sandhill/utils/filters.py) file. Some examples are: 
* `solr_escape`: A custom filter, which will take a value and escape the special Solr characters
* `urlencode`: Encode the value to be used in a URL



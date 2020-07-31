Metadata Configuration
---------------
This document describes how to manage the metadata display on 
item pages within Sandhill.

Define the Configuration File
============================================
Files must be named after the namespace (ex: `etd.json`) or 
based on the mime type, replacing the `\` with `_` 
(ex: `application_pdf.json`). 

The namespace configuration will always be prefered if it exists 
but otherwise it will look for the mime type config. For example,
you could have ETDs use a specific metadata configuration while the 
rest of the PDF objects use a generic PDF metadata configuration.


Field Definitions
================
Sample configuration:  
```
{
    "mime_types" : [ "application/pdf" ],
    "title_field": "fgs_label_s",
    "media_template": "media_display/preview.html.j2",
    "embargo_field": "embargo_end_date_ss",
    "display": [
        {
            "field": "description",
            "name": "Summary",
            "metadata_template": "item_page_blocks/metadata_expand_block.html.j2",
            "limit_length": 500
        },
        {
            "field": "collection_t",
            "name": "In Collections",
            "metadata_template": "item_page_blocks/metadata_descriptive_list.html.j2",
            "link": "/{{ view_args.namespace }}"
        },
        {
            "field": "genre_aat",
            "name": "Material Type",
            "metadata_template": "item_page_blocks/metadata_descriptive_list.html.j2"
        },
        {
            "field": "name_author",
            "name": "Authors",
            "metadata_template": "item_page_blocks/metadata_descriptive_list.html.j2",
            "link": "/search?fq=name_author:{{ metadata_value | solr_escape | urlencode }}"
        }
    ],
}
```
General:  
* `mim_types`: list of the mime types that this configuration should apply to
* `title_field`: The Solr field to use for the title on the item page
* `media_template`: The template file within the `sandhill\templates` directory to use for the object viewer
* `embargo_field`: The Solr field to check if the object is embargoed

Display (`display`):
These are the fields that appear in the metadata section of the item page
* `field`: Solr field to display the value of
* `name`: The label to use for the field
* `metadata_template`: The template file within the `sandhill\templates` directory to display this field
* (Optional) `link`: If provided, will turn the metadata value into a link. See the [variables](#variables) section below 
for more information
* (Optional) `limit_length`: The max length of the field allowed, depending on the `metada_template` provided, it will either
truncate the value or create an expanding box

Variables
============
The `link` field within the `display` section has the ability to create dynamic URLs with variables 
used through out the page. Some examples of variables available are: 
* `metadata_value` which is the value of the current metadata field
* `view_args.namespace` and `view_args.id` come from the route configs in the `routes` section and 
represent the pid components

Additionally, you can dynamically alter the values of the variables used by using Jinja2 filters. To add 
to the existing Jinja2 filters, there are custom ones available within our [filters](https://gitlab.msu.edu/msu-libraries/repo-team/sandhill/-/blob/master/sandhill/utils/filters.py) file. Some examples are: 
* `solr_escape`: Which will take a value and escape the special Solr characters
* `urlencode`: Encode the value to be used in a URL

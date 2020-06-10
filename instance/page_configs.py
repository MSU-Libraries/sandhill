{
    {
        "node-name": "about",
        "required-data": [
            "[variable]": "[api-url]",
            "[variable2]": "[api-url2]"
        ],
        "template": "[template.html.j2]"
    },
    {
        "node-name": "etd"
    }
    {
        "node-name": "search"
        "required-data": [
            "facet-data": "/solr/blah=blah",
            "search-results": "/solr/q=?"
        ]
    },
    {
        "node-name": "item"
        "required-data": [
            "metadata": "/solr/blah=blah"
        ]
    }
}

# Searching on Sandhill

The Sandhill search box passes queries directly to Solr's [edismax](https://lucene.apache.org/solr/guide/7_0/the-extended-dismax-query-parser.html) query parser with the `q` field, allowing for the full use  of Solr's query syntax in the input box. By default, the `edismax` search will query the set of fields specified in Solr configs.

For multi-word search queries, all words must be present for a positive result.

## Booleans and Other Operators

The `edismax` syntax supports `AND`, `OR`, and `NOT` as Boolean operators, which must be written as shown in all caps to work as expected. Also supported are similar terms `+` (to indicate that a term *must* be present in results) and `-` (to indicate a term that must *not* be present).

[frogs AND toads](http://sandhill.devel.lib.msu.edu/search?q=frogs+AND+toads) vs. [frogs OR toads](http://sandhill.devel.lib.msu.edu/search?q=frogs+OR+toads)  
[frogs AND NOT frogs](http://sandhill.devel.lib.msu.edu/search?q=frogs+AND+NOT+frogs) (returns the expected 0 results)

Wildcard searches can be performed with the `*` character, which matches any sequence of 0 or more characters, and the `?` character, which matches any single character.

[frog* -frog -frogs](http://sandhill.devel.lib.msu.edu/search?q=frog*+-frog+-frogs) (searches for any words starting with "frog" but that aren't "frog" or "frogs" — I checked and we get results for "frogging", "froggy", "frog2" (software), and "frogy" (OCR error), etc.)

## Search Length

The maximum search length in Sandhill is set at 4096 characters, which should be ample enough to insure that any long dissertation title can be accommodated. This limit applies just to the search box - it's possible to paste longer text directly into the url up to the limit of the responding server, above which a `414` error code is returned.

## Fuzzy and Proximity Searching

[Fuzzy search](https://lucene.apache.org/solr/guide/7_0/the-standard-query-parser.html#fuzzy-searches)  
[Proximity search](https://lucene.apache.org/solr/guide/7_0/the-standard-query-parser.html#proximity-searches)

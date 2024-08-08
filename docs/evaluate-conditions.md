# Evaluate Conditions
Sandhill comes with a means of defining a complex true/false evaluation, which is sometimes useful
when creating a site.

This might be helpful if your site needs to:

 - Determine if a resource is restricted or not.
 - Select a different set of templates to display depending on context variables.

Accessing the evaluate ability in Sandhill can be done via the
[`evaluate.conditions`](/sandhill/data-processors/#sandhill.processors.evaluate.conditions)
data processor.

## Example
Here is an example entry in our route's `data` list for the `evaluate.conditions` processor.
```json
{
  "name": "myeval",
  "processor": "evaluate.conditions",
  "conditions": "access_checks.record",
  "match_all": true
}
```
The `conditions` indicates where in our `data` to search for the list of conditions to evaluate.

The `match_all` set to `true` indicates that all of the conditions much be truthy in order for
this evaluate to be considered a success (i.e. return `True`).

Assume our `data` already has appropriate entries, such as:
```json
{
  "record": { "...": "..." },
  "access_checks": {
    "records": [
      {
        "evaluate": "{{ record.copyright_status }}",
        "match_when": ["public domain", "permission granted"]
      },
      {
        "evaluate": "{{ record.locked_status }}",
        "match_when_not": ["unpublished", "editing"]
      },
      {
        "evaluate": "{{ record.title | length > 0 }}",
        "match_when": ["True"]
      }
    ]
  }
}
```

There three conditions to check above within the `access_checks.records` keys indicated
by our `conditions` value.

Each condition must have:

* An `evaluate` key with a string expression. All `evaluate` expressions will be rendered by Jinja before being checked against.
* Either of:
  - A `match_when` key containing a list of values, one of which must equal the rendered `evaluate` to be considered a success.
  - A `match_when_not` key containing a list of values, none of which must equal the rendered `evaluate` to be considered a success.

As we have `match_all` set to `true`, all three of our above conditions much succeed in order for
our `evaluate.conditions` data processor return `True`. If any condition is not true, the whole data processor
will return `False`. If we only cared that any single condition be true, we could set `match_all` to `false`.

## Abort on Match
You can optionally have Sandhill instantly abort if an `evaluate.conditions` is successful by
setting `abort_on_match` in your data processor entry to `true`.

```json
{
  "name": "myeval",
  "processor": "evaluate.conditions",
  "conditions": "access_checks.record",
  "match_all": true,
  "abort_on_match": true,
  "on_fail": 401
}
```

If the evaluate succeeds, Sandhill will trigger an abort to an error page. The default
HTTP code is `503` but this can be customized by setting an `on_fail` for the data
processor as seen in the above example.

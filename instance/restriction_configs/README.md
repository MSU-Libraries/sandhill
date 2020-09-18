# Restriction Conditions

`restriction_conditions` determines if any restrictions can be applied to the item.

`restriction_conditions` is a list of dicts.

Example:
```
    "restriction_conditions": [
        {
            "evaluate": "{{ item.embargo_end_date_ss | head | date_passed if item.embargo_end_date_ss is defined else False }}",
            "match_when": ["True"]
        }
    ]
```
* `evaluate`: This is the value in the current context to be compared to match_when values. This string is rendered through Jinja before comparison.
* `match_when`: List of acceptable values, these values are compared with the provided value to determine a match. Matches must be exact.


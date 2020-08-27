from sandhill.processors import evaluate

def test_conditions():
    data_dict = {
        "name": "restriction",
        "processor": "evaluate.conditions",
        "on_fail": 401,
        "conditions": "metadata_conf.restriction_conditions",
        "match_all": True,
        "metadata_conf": {
            "restriction_conditions": [
                {
                    "value": "test",
                    "allowed": ["test"]
                }
            ]
        }
    }

    # Test for positive evalution match in the data_dict
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is True

    # Test for negative unmatched condition
    del data_dict['metadata_conf']
    data_dict['conditions'] = "other_conf.other_cons"
    data_dict['other_conf'] = {
        "other_cons": [
            {
                "value": "notmatched",
                "allowed": ["will", "fail"]
            }
        ]
    }
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is False

    # Test for matching only 1 of multiple conditions with match_all = True
    data_dict['other_conf'] = {
        "other_cons": [
            {
                "value": "test",
                "allowed": ["test"]
            },
            {
                "value": "notmatched",
                "allowed": ["will", "fail"]
            }
        ]
    }
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is False

    # Test for matching any of multiple conditions
    data_dict['match_all'] = False
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is True

    # Test for abort on match
    data_dict['abort_on_match'] = True
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is None

    # Test for missing definition of 'match_all'
    del data_dict['match_all']
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is None

    # Test for missing 'conditions' definitions
    data_dict['match_all'] = False
    del data_dict['conditions']
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is None

    # Test referencing an invalid condition key
    data_dict['conditions'] = "other_conf.invalid_key"
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is None

    # Test for missing conditions 'value'/'allowed' dict
    data_dict['conditions'] = "other_conf.other_cons"
    del data_dict['other_conf']
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is None


def test_template():
    data_dict = {
        'processor': 'evaluate.template',
        'name': 'datastream_label',
        'test_var': 'test_val',
        'value': '{{ test_var }}',
        'on_fail': 500
    }

    # Test for positive scenario
    evaluation = evaluate.template(data_dict)
    assert isinstance(evaluation, str)
    assert evaluation == 'test_val'

    # Test for invalid template passed
    data_dict['value'] = "{{ forgot to close"
    evaluation = evaluate.template(data_dict)
    assert evaluation is None

    # Test for invalid variable in valid jinja
    data_dict['value'] = "{{ invalid_var_name }}"
    evaluation = evaluate.template(data_dict)
    assert isinstance(evaluation, str)
    assert evaluation == ''

    # Test not providing a 'value'
    del data_dict['value']
    evaluation = evaluate.template(data_dict)
    assert evaluation is None

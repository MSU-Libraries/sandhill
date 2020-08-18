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

    # Test for missing definition of 'match_all'
    del data_dict['match_all']
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is None

    # Test for missing 'conditions' definitions
    del data_dict['conditions']
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is None

    # Test for missing conditions 'value'/'allowed' dict
    data_dict['conditions'] = "other_conf.other_cons"
    del data_dict['other_conf']
    data_dict['match_all'] = True
    evaluation = evaluate.conditions(data_dict)
    assert evaluation is None


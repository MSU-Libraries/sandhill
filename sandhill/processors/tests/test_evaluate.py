from sandhill import app
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
                    "evaluate": "test",
                    "match_when": ["test"]
                }
            ]
        }
    }

    with app.app_context():
        # Test for positive evalution match in the data_dict
        evaluation = evaluate.conditions(data_dict)
        assert evaluation is True

    # Test for negative unmatched condition
    del data_dict['metadata_conf']
    data_dict['conditions'] = "other_conf.other_cons"
    data_dict['other_conf'] = {
        "other_cons": [
            {
                "evaluate": "notmatched",
                "match_when": ["will", "fail"]
            }
        ]
    }
    with app.app_context():
        evaluation = evaluate.conditions(data_dict)
        assert evaluation is False

    # Test for matching only 1 of multiple conditions with match_all = True
    data_dict['other_conf'] = {
        "other_cons": [
            {
                "evaluate": "test",
                "match_when": ["test"]
            },
            {
                "evaluate": "notmatched",
                "match_when": ["will", "fail"]
            }
        ]
    }
    with app.app_context():
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

        # Test for missing conditions 'evaluate'/'match_when' dict
        data_dict['conditions'] = "other_conf.other_cons"
        del data_dict['other_conf']
        evaluation = evaluate.conditions(data_dict)
        assert evaluation is None

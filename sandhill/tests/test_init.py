'''
Test the __init__.py file
'''
from unittest import mock
import sandhill

def test_init():
    '''
    Tests the init function
    '''
    with mock.patch.object(sandhill, "main", return_value=42):
        with mock.patch.object(sandhill, "__name__", "__main__"):
            with mock.patch.object(sandhill.app, 'run') as mock_exit:
                sandhill.init()
                assert mock_exit._mock_call_args.__str__() == 'call(debug=True)' # pylint: disable=protected-access

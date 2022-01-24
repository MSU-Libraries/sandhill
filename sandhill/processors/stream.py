'''
Processor for streaming data
'''
from flask import abort, Response as FlaskResponse
from requests.models import Response as RequestsResponse
from sandhill import app
from sandhill.utils.error_handling import dp_abort

def response(data):
    '''
    Stream a Requests library response stored in data with the key of stream_var
    args:
        data (dict): The route_config 'data' section
    returns:
        streams the response
    '''
    allowed_headers = [
        'Content-Type', 'Content-Disposition', 'Content-Length',
        'Range', 'accept-ranges', 'Content-Range'
    ]
    if 'response' not in data:
        app.logger.error("stream.response requires a 'response' variable to be set.")
        abort(500)
    resp = data[data["response"]] if data["response"] in data else None

    # Not a valid response
    if not isinstance(resp, RequestsResponse):
        dp_abort(503)
        return None
    # Valid response, but not a success (bool check on resp fails if http code is 400 to 600)
    if not resp:
        dp_abort(resp.status_code)
        return None

    stream_response = FlaskResponse(
        resp.iter_content(chunk_size=app.config['STREAM_CHUNK_SIZE']),
        status=resp.status_code
    )
    for header in resp.headers.keys():
        # Case insensitive header matching
        if header.lower() in [allowed_key.lower() for allowed_key in allowed_headers]:
            stream_response.headers.set(header, resp.headers.get(header))
    return stream_response

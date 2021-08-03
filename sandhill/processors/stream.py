'''
Processor for streaming data
'''
from flask import abort, Response as FlaskResponse
from requests.models import Response as RequestsResponse
from sandhill import app

def stream(data_dict):
    '''
    Stream the response stored in data with the key of stream_var
    args:
        data_dict (dict): The route_config 'data' section
    returns:
        streams the response
    '''
    allowed_headers = [
        'Content-Type', 'Content-Disposition', 'Content-Length',
        'Range', 'accept-ranges', 'Content-Range'
    ]
    if 'stream' not in data_dict or data_dict['stream'] not in data_dict:
        app.logger.error((
            "stream variable: 'stream' not set in config, or references"
            "unavailable stream. Unable to stream response."
        ))
        abort(500)
    resp = data_dict[data_dict["stream"]]
    if isinstance(resp, RequestsResponse) and not resp:
        abort(resp.status_code)
    elif not resp:
        abort(503)
    stream_response = FlaskResponse(
        resp.iter_content(chunk_size=app.config['STREAM_CHUNK_SIZE']),
        status=resp.status_code
    )
    for header in resp.headers.keys():
        # Case insensitive header matching
        if header.lower() in [allowed_key.lower() for allowed_key in allowed_headers]:
            stream_response.headers.set(header, resp.headers.get(header))
    return stream_response

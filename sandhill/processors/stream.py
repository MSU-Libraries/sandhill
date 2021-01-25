'''
Processor for streaming data
'''
import io
from sandhill import app
from flask import request, render_template, abort, Response as FlaskResponse

def stream(data_dict):
    '''
    Stream the response stored in data with the key of stream_var
    args:
        data_dict (dict): The route_config 'data' section
    returns:
        streams the response
    '''
    allowed_headers = ['Content-Type', 'Content-Disposition', 'Content-Length']
    if 'stream' not in data_dict:
        app.logger.error("stream variable: 'stream' not set in config. Unable to stream response.")
        abort(500)
    resp = data_dict[data_dict["stream"]]
    if isinstance(resp, RequestsResponse) and not resp:
        abort(resp.status_code)
    elif not resp:
        abort(503)

    stream = FlaskResponse(resp.iter_content(chunk_size=app.config['STREAM_CHUNK_SIZE']))
    for header in allowed_headers:
        if header in resp.headers.keys():
            stream.headers.set(header, resp.headers.get(header))
    return stream

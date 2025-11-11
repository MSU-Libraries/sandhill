'''
Processor for streaming data
'''
from flask import abort, make_response, Response as FlaskResponse
from pathlib import Path
from requests.models import Response as RequestsResponse
from sandhill import app
from sandhill.utils.response import file_to_response
from sandhill.utils.error_handling import dp_abort

def response(data):
    '''
    Stream a Requests library response that was previously loaded. \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `response` _str_: The key where the response is located.\n
            * Key from `data[response]` _requests.Response_: The response to stream.\n
    Returns:
        (flask.Response|None): A stream of the response \n
    Raises:
        wergzeug.exceptions.HTTPException: If `on_fail` is set. \n
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

def serve_file(data):
    '''
    Stream a file as a response. \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `file_to_serve` _str_: Filepath of the file to serve.\n
    Returns:
        (flask.Response|None): A stream of the response \n
    Raises:
        wergzeug.exceptions.HTTPException: If `on_fail` is set. \n
    '''

    if 'file_to_serve' not in data:
        app.logger.error("stream.serve_file requires a 'file_to_serve' variable to be set.")
        dp_abort(500)

    file = Path(data['file_to_serve'])

    if not file.exists():
        app.logger.error("stream.serve_file file \"{data['file_to_serve']}\" does not exist.")
        dp_abort(500)

    stream = open(file, 'rb')
    mimetype = data['mimetype'] if 'mimetype' in data else 'application/octet-stream'

    return file_to_response(stream, mimetype)

def string(data):
    '''
    Stream a data variable as string data to the output \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `var` _str_: The name of the variable whose content should be sent.\n
            * `mimetype` _str_: The mimetype to send for the data (default: text/plain).\n
    Returns:
        (flask.Response|None): A stream of the response \n
    '''
    if 'var' not in data or not data.get(data['var']):
        app.logger.error("requires that 'var' is set to name of non-empty data variable")
        abort(500)
    mimetype = data.get('mimetype', 'text/plain')

    string_response = make_response(data.get(data['var']))
    string_response.mimetype = mimetype
    return string_response

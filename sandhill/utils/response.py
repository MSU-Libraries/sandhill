"""
Functions for handling responses.
"""
import io

from pathlib import Path
from flask import Response

def to_response(string: str, content_type: str="text/plain") -> Response:
    """
    Take a string and return it as a flask response with the given mimetype.
    Args:
        string (str): The string to return as a response.\n
        content_type (str): Response content type.\n
    Returns:
        (Response): The Flask response containing the string. \n
    """
    return Response(string, content_type=content_type)

def file_to_response(resource: io.IOBase, mimetype: str= "application/octet-stream") -> Response:
    """
        Take an opened resource (zip file) and return a Flask Response.
        Args:
            resource (io.IOBase): The file being opened to return as a response to be downloaded.\n
            mimetype (str): Mimetype returned in the response.\n
        Returns:
            (Response): The Flask response containing the string. \n
        """
    file = Path(resource.name)
    # 'Content-Encoding': 'Identity' => Allow Content-Length to be kept;
    # Tell the browser not to do additional compression
    return Response(
        resource,
        mimetype=mimetype,
        headers={
            'Content-Length': str(file.stat().st_size),
            'Content-Disposition': f'attachment; filename="{file.name}"',
            'Content-Encoding': 'Identity'
        },
        direct_passthrough=True
    )

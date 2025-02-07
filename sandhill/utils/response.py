"""
Functions for handling responses.
"""
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

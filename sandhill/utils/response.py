"""
Functions for handling responses.
"""
from flask import Response

def to_response(str: str, content_type: str="text/plain") -> Response:
    return Response(str, content_type=content_type)

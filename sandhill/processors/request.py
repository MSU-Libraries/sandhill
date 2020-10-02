from flask import request


def get_url_components(data_dict):
    """Get current url and return dictionary of components."""
    url_components = {
        "path": request.path,
        "full_path": request.full_path,
        "base_url": request.base_url,
        "url": request.url,
        "query_args": request.args.to_dict(flat=False)
    }
    return url_components

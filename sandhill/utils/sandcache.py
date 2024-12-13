"""
The Sand Cache; quick access to data stored on disk
"""
import os
import tempfile
from contextlib import contextmanager
from diskcache import Cache
from sandhill import app

@contextmanager
def sandcache():
    """
    Opens the default diskcache cache for Sandhill
    """
    cachedir = os.path.join(tempfile.gettempdir(), 'crane-cache')
    cache = Cache(cachedir, size_limit=app.config.get('DISKCACHE_SIZE_GB', 1) * 1024**3)
    try:
        yield cache
    finally:
        cache.close()

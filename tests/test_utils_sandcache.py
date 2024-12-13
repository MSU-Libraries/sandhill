from sandhill.utils.sandcache import sandcache

def test_sandcache():
    with sandcache() as cache:
        cache.clear()
        assert cache.get('data') is None
        cache['data'] = "Data one"
        assert cache.get('data') == "Data one"

    with sandcache() as cache:
        assert "Data one" == cache['data']
        del cache['data']
        assert cache.get('data') is None
        cache.clear()

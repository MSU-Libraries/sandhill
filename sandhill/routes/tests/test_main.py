from sandhill import app

def test_home():
    client = app.test_client()
    result = client.get('/')
    assert result.status_code == 200

def test_404():
    client = app.test_client()
    result = client.get('/invalid/page/route')
    assert result.status_code == 404

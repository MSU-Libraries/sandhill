from sandhill import app

def test_home():
    client = app.test_client()
    result = client.get('/')
    assert result.status_code == 200

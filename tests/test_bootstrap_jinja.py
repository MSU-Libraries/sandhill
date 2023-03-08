from sandhill import app

def test_configure_jinja():
    #with app.test_request_context("/"):
    with app.test_client() as client:
        assert app.jinja_env.trim_blocks == True
        assert app.jinja_env.lstrip_blocks == True

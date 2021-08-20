from sandhill.utils import html

def test_HTMLTagFilter():
    allowed = ['a', 'b']
    htf = html.HTMLTagFilter(allow=allowed)
    htf.feed("<html><body><h1>Hello!</h1><div class='main'>This is a <a " \
              "href='http://example.com'>great place</a> to <b>be</b> and " \
              "<i>stuff</i>.</div></body></html>")
    expected_out = "Hello!This is a <a href=\"http://example.com\">great place</a>" \
                   " to <b>be</b> and stuff."
    assert htf.output == expected_out


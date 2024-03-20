from sandhill.utils import html

def test_HTMLTagFilter():
    # Testing tag filtering
    allowed = ['a', 'b']
    htf = html.HTMLTagFilter(tags=allowed)
    htf.feed("<html><body><h1>Hello!</h1><div class='main'>This is a <a " \
              "href='http://example.com'>great place</a> to <b>be</b> and " \
              "<i>stuff</i>.</div></body></html>")
    expected_out = "Hello!This is a <a href=\"http://example.com\">great place</a>" \
                   " to <b>be</b> and stuff."
    assert htf.output == expected_out

    # Testing handling of entities
    htf = html.HTMLTagFilter(tags=[])
    htf.feed("<html><body>First just plain amper A&B " \
             "next encoded named amper C&amp;D " \
             "next charref amper E&#38;F" \
             "</body></html>")
    expected_out = "First just plain amper A&amp;B " \
                   "next encoded named amper C&amp;D " \
                   "next charref amper E&#38;F"
    assert htf.output == expected_out


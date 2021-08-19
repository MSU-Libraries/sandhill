'''
HTML utilities and support classes
'''
import html
from html.parser import HTMLParser

class HTMLTagFilter(HTMLParser):
    """
    Filter through HTML and remove all tags except for those allowed.
    """
    def __init__(self, allow: list):
        super().__init__()
        self.tags = allow
        self.output = ""

    def handle_starttag(self, tag, attrs):
        if tag in self.tags:
            attrstr = " ".join([
                "%s=\"%s\"" % (attr[0], html.escape(attr[1], quote=True))
                for attr in attrs
            ])
            attrstr = " " * bool(attrstr) + attrstr
            self.output += f"<{tag}{attrstr}>"

    def handle_endtag(self, tag):
        if tag in self.tags:
            self.output += f"</{tag}>"

    def handle_data(self, data):
        self.output += data

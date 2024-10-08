'''
HTML utilities and support classes
'''
import html
from html.parser import HTMLParser

class HTMLTagFilter(HTMLParser):
    """
    Class used to filter through HTML and remove all tags except for those set as allowed. \n
    Used by the `filtertags()` template filter. \n
    """
    def __init__(self, tags: list):
        super().__init__(convert_charrefs=False)
        self._tags = tags
        self.output = ""

    def handle_starttag(self, tag, attrs):
        """Handle open tags"""
        if tag in self._tags:
            attrstr = " ".join([
                f"{attr[0]}=\"{html.escape(attr[1], quote=True)}\""
                for attr in attrs
            ])
            attrstr = " " * bool(attrstr) + attrstr
            self.output += f"<{tag}{attrstr}>"

    def handle_endtag(self, tag):
        """Handle close tags"""
        if tag in self._tags:
            self.output += f"</{tag}>"

    def handle_data(self, data):
        """Handle text data"""
        self.output += data

    def handle_entityref(self, name):
        """Handle escape entities"""
        # Handle case where no semicolon exists after &name (HTMLParser still treats as entref)
        # pylint: disable=unnecessary-semicolon
        self.output += f"&{name};" \
            if self.rawdata.startswith(f"&{name};", self.offset) \
            else f"&amp;{name}"

    def handle_charref(self, name):
        """Handle escape chars"""
        self.output += f"&#{name};"

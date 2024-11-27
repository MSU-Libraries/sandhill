"""
Solr related functionality.
"""
import re

class Solr:
    """
    Class for handling Solr related logic, such as encoding/decoding.
    """
    _escape_chars_all = {'*': r'\*', '?': r'\?', '-': r'\-', '&': r'\&', '|': r'\|', \
        '!': r'\!', '(': r'\(', ')': r'\)', '{': r'\{', '}': r'\}', '[': r'\[', ']': r'\]', \
        '^': r'\^', '~': r'\~', ' ': r'\ ', '+': r'\+', ':': r'\:', '"': r'\"', ';': r'\;'}
    _escape_chars_all_re = re.compile('|'.join(re.escape(key) for key in _escape_chars_all))
    _escape_chars_nowild = dict(list(_escape_chars_all.items())[2:])
    _escape_chars_nowild_re = re.compile('|'.join(re.escape(key) for key in _escape_chars_nowild))

    def __init__(self):
        self._scanner = None

        # Variables for query parsing
        self._tokens = None
        self._pos = None
        self._stack = None

    def _init_scanner(self):
        """
        Initialize the token scanner for parsing a query \n
        """
        # TODO filter()
        self._scanner = re.Scanner([
            (r'"', \
                lambda scanner, token: ("QUOTE", token)),
            (r'[\[\]]', \
                lambda scanner, token: ("RANGE", token)),
            (r'[()]', \
                lambda scanner, token: ("PAREN", token)),
            (r'(AND|OR|&&|\|\||NOT)', \
                lambda scanner, token: ("LOGIC", token)),
            (r'[*?]', \
                lambda scanner, token: ("WILD", token)),
            (r'[-+]', \
                lambda scanner, token: ("PLMS", token)),
            (r'[^-+\[\]?*()"\s]+', \
                lambda scanner, token: ("TERM", token)),
            (r'\s+', \
                lambda scanner, token: ("SPACE", token)),
        ])

    def _tokenize_query(self, query):
        """
        Tokenize a query, resetting stack and stack position \n
        """
        self._init_scanner()
        self._tokens, _ = self._scanner.scan(query)
        self._pos = 0
        self._stack = []

    def _prev_token(self):
        ppair = (None, None)
        if self._pos > 0:
            ppair = self._tokens[self._pos - 1]
        return ppair

    def _prev_token_is(self, token_id):
        return self._prev_token()[0] == token_id

    def _get_token(self):
        for pos, tpair in enumerate(self._tokens):
            self._pos = pos
            yield tpair

    def _next_token(self):
        npair = (None, None)
        if self._pos + 1 < len(self._tokens):
            npair = self._tokens[self._pos + 1]
        return npair

    def _next_token_is(self, token_id):
        return self._next_token()[0] == token_id

    def _in_stack(self, *args):
        """
        Check if ANY of the given arguments are in the _stack \n
        Args:
            *args (string): token_id's to check the stack for \n
        Returns:
            (bool) Returns True if ANY of the provided args are found in the _stack \n
        """
        return any(arg in self._stack for arg in args)

    def _stack_top_is(self, token_id):
        """
        Checks that the top of the stack is the given token. An empty stack never matches. \n
        Args:
            token_id (str): the token to match \n
        Returns:
            (bool) True if matched \n
        """
        return self._stack and self._stack[-1] == token_id

    def _stack_entry(self, token_id, token):
        """
        Process the given stackable token_id \n
        Args:
            token_id (str): the token_id to process \n
            token (str): the token string \n
        Raises:
            ValueError when attempting to close a token pair that hasn't been opened \n
        """
        if token in tuple("[("):
            self._stack.append(token_id)
        elif self._stack_top_is(token_id):
            self._stack.pop()
        else:
            raise ValueError(f"Cannot close {token_id}; no matching pair.")

    def encode_query(self, query, escape_wildcards=False):
        """
        Given a solr query, parse and encode characters as appropriate \n
        Args:
            query (str): the solr query \n
            escape_wildcards (bool): Whether to escape * and ? \n
        Returns:
            (str) the encoded solr query \n
        """
        self._tokenize_query(query)
        encoded = ""
        for tid, tok in self._get_token():
            if tid == "QUOTE" and not self._in_stack("QUOTE"):
                self._stack.append(tid)
            elif self._in_stack("QUOTE"):
                if tid == "QUOTE":
                    self._stack.pop()
            elif tid == "RANGE":
                self._stack_entry(tid, tok)
            elif tid == "TERM" and not self._in_stack("QUOTE", "RANGE"):
                tok = self.encode_value(tok)
            elif tid == "PLMS" and self._prev_token_is("TERM") and not self._in_stack("RANGE"):
                tok = self.encode_value(tok)
            elif tid == "WILD":
                tok = self.encode_value(tok, escape_wildcards)
            elif tid == "PAREN":
                self._stack_entry(tid, tok)

            encoded += tok

        if self._stack:
            raise ValueError(f"Unmatched {self._stack[-1]} pair detected in: {query}")

        return encoded

    def encode_value(self, value, escape_wildcards=False):
        """
        Given a value, encode characters as appropriate for use in a Solr query \n
        Args:
            query (str): the value to encode \n
            escape_wildcards (bool): Whether to encode * and ? \n
        Returns:
            (str) the encoded value \n
        """
        escapes = Solr._escape_chars_all
        escape_re = Solr._escape_chars_all_re
        if not escape_wildcards:
            escapes = Solr._escape_chars_nowild
            escape_re = Solr._escape_chars_nowild_re

        def replace(matches):
            return escapes[matches.group(0)]

        value = value.replace('\\', r'\\')  # must be first replacement
        return escape_re.sub(replace, value)

    def decode_value(self, value, escape_wildcards=False):
        """
        Given a value already encoded for use in a Solr query, decode the \
        characters back to a normal string \n
        Args:
            query (str): the value to decode \n
            escape_wildcards (bool): Whether to decode * and ? \n
        Returns:
            (str) the decoded value \n
        """
        escapes = Solr._escape_chars_all
        if not escape_wildcards:
            escapes = Solr._escape_chars_nowild

        for key, val in escapes.items():
            value = value.replace(val, key)
        return value.replace(r'\\', '\\')  # must be last replacement

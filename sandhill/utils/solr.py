"""
Solr related functionality
"""
import re

class Solr:
    """
    Class for handling Solr related logic, like encoding/decoding
    """
    def __init__(self):
        self.scanner = None
        self.char_escapes = {' ': r'\ ', '+': r'\+', '-': r'\-', '&': r'\&', '|': r'\|', \
            '!': r'\!', '(': r'\(', ')': r'\)', '{': r'\{', '}': r'\}', '[': r'\[', ']': r'\]', \
            '^': r'\^', '~': r'\~', '*': r'\*', '?': r'\?', ':': r'\:', '"': r'\"', ';': r'\;'}

        # Variables for query parsing
        self._tokens = None
        self._pos = None
        self._stack = None

    def _init_scanner(self):
        """
        Initialize the token scanner for parsing a query
        """
        # TODO filter()
        self.scanner = re.Scanner([
            (r'"', \
                lambda scanner, token: ("QUOTE", token)),
            (r'[[\]]', \
                lambda scanner, token: ("RANGE", token)),
            (r'[()]', \
                lambda scanner, token: ("PAREN", token)),
            (r'(AND|OR|&&|\|\||NOT)', \
                lambda scanner, token: ("LOGIC", token)),
            (r'[*?]', \
                lambda scanner, token: ("WILD", token)),
            (r'[-+]', \
                lambda scanner, token: ("PLMS", token)),
            (r'[^-+[\]?*()"\s]+', \
                lambda scanner, token: ("TERM", token)),
            (r'\s+', \
                lambda scanner, token: ("SPACE", token)),
        ])

    def _tokenize_query(self, query):
        """
        Tokenize a query, resetting stack and stack position
        """
        self._init_scanner()
        self._tokens, _ = self.scanner.scan(query)
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
        Check if ANY of the given arguments are in the _stack
        args:
            *args (string): token_id's to check the stack for
        returns:
            (bool) Returns True if ANY of the provided args are found in the _stack
        """
        return any(arg in self._stack for arg in args)

    def _stack_top_is(self, token_id):
        """
        Checks that the top of the stack is the given token. An empty stack never matches.
        args:
            token_id (str): the token to match
        returns:
            (bool) True if matched
        """
        return self._stack and self._stack[-1] == token_id

    def _stack_entry(self, token_id, token):
        """
        Process the given stackable token_id
        args:
            token_id (str): the token_id to process
            token (str): the token string
        raises:
            ValueError when attempting to close a token pair that hasn't been opened
        """
        if token in tuple("[("):
            self._stack.append(token_id)
        elif self._stack_top_is(token_id):
            self._stack.pop()
        else:
            raise ValueError(f"Cannot close {token_id}; no matching pair.")

    def encode_query(self, query, escape_wildcards=False):
        """
        Given a solr query, parse and encode characters as appropriate
        args:
            query (str): the solr query
            escape_wildcards (bool): Whether to escape * and ?
        returns:
            (str) the encoded solr query
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
        Given a value, encode characters as appropriate for use in a Solr query
        args:
            query (str): the value to encode
            escape_wildcards (bool): Whether to encode * and ?
        returns:
            (str) the encoded value
        """
        escapes = self.char_escapes.copy()
        if not escape_wildcards:
            del escapes['*']
            del escapes['?']
        value = value.replace('\\', r'\\')  # must be first replacement
        for key, val in escapes.items():
            value = value.replace(key, val)
        return value

    def decode_value(self, value, escape_wildcards=False):
        """
        Given a value already encoded for use in a Solr query, decode the
        characters back to a normal string
        args:
            query (str): the value to decode
            escape_wildcards (bool): Whether to decode * and ?
        returns:
            (str) the decoded value
        """
        escapes = self.char_escapes.copy()
        if not escape_wildcards:
            del escapes['*']
            del escapes['?']
        for key, val in escapes.items():
            value = value.replace(val, key)
        value = value.replace(r'\\', '\\')  # must be last replacement
        return value

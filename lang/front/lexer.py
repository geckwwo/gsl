import string
import enum

class TokenType(enum.Enum):
    IDEN = 1
    INT = 2
    FLOAT = 3
    STR = 4
    KEYWORD = 5
    NULL = 6

    LPAR = "("
    RPAR = ")"
    LCUR = "{"
    RCUR = "}"
    LBRK = "["
    RBRK = "]"

    SEMICOLON = ";"
    DOT = "."
    COMMA = ","

    PLUS = 10
    MINUS = 11
    MUL = 12
    DIV = 13
    MOD = 14

    INLINE_PLUS = 1010
    INLINE_MINUS = 1011
    INLINE_MUL = 1012
    INLINE_DIV = 1013
    INLINE_MOD = 1014

    ASSIGN = 20

    EQ = 30
    NEQ = 31
    LT = 32
    LTE = 33
    GT = 34
    GTE = 35
    LOGAND = 36
    LOGOR = 37
    LOGXOR = 38
    NOT = 39

    
    AND = 41
    OR = 42
    XOR = 43

class Keyword(enum.Enum):
    IF = "if"
    ELSE = "else"
    ELSEIF = "elseif"
    WHILE = "while"
    FOR = "for"
    FOREACH = "foreach"
    IN = "in"
    BREAK = "break"
    RETURN = "return"
    FUN = "fun"

class Token:
    def __init__(self, token_type, value, rel=None, line=None):
        self.type = token_type
        self.value = value
        self.rel = rel
        self.line = line
    def __repr__(self):
        return f"<{self.type}" + (">" if self.value is None else f": {self.value}>")

class Lexer:
    def __reset(self, text):
        self.text = text + "\n"
        self.ch = None
        self.idx = -1
        self.rel = 0
        self.line = 1
        self.tokens = []

    def next(self, step=1):
        self.idx += step
        self.rel += step
        self.ch = self.text[self.idx] if self.idx < len(self.text) else None
        if self.ch == "\n":
            self.rel = 1
            self.line += 1

    def token(self, token_type, value=None, rel=None, line=None):
        self.tokens.append(Token(token_type, value, rel if rel is not None else self.rel, line if line is not None else self.line))

    def run(self, text):
        self.__reset(text)
        self.next()
        while self.ch is not None:
            if self.ch in TokenType:
                self.token(TokenType(self.ch))
                self.next()
            elif self.ch in "\r\n\t\v ":
                self.next()
            elif self.ch in "0123456789":
                num = ""
                rel = self.rel
                while self.ch in "0123456789_.":
                    num += self.ch
                    self.next()
                if "." in num:
                    self.token(TokenType.FLOAT, float(num), rel)
                else:
                    self.token(TokenType.INT, int(num), rel)
            elif self.ch in "+-*/%":
                mp = {"+": "PLUS", "-": "MINUS", "*": "MUL", "/": "DIV", "%": "MOD"}[self.ch]
                self.next()
                if self.ch == "=":
                    self.token(getattr(TokenType, "INLINE_" + mp, rel=self.rel-1))
                    self.next()
                else:
                    self.token(getattr(TokenType, mp), rel=self.rel-1)
            elif self.ch == "=":
                self.next()
                if self.ch == "=":
                    self.token(TokenType.EQ, rel=self.rel-1)
                    self.next()
                else:
                    self.token(TokenType.ASSIGN, rel=self.rel-1)
            elif self.ch == "!":
                self.next()
                if self.ch == "=":
                    self.token(TokenType.NEQ, rel=self.rel-1)
                    self.next()
                else:
                    self.token(TokenType.NOT, rel=self.rel-1)
            elif self.ch in string.ascii_letters + "_":
                iden = ""
                rel = self.rel
                while self.ch in string.ascii_letters + "_1234567890":
                    iden += self.ch
                    self.next()
                if iden not in Keyword:
                    self.token(TokenType.IDEN, iden, rel=rel)
                elif iden.lower() == "null":
                    self.token(TokenType.NULL, rel=rel)
                else:
                    self.token(TokenType.KEYWORD, Keyword(iden), rel=rel)
            elif self.ch in "\"'":
                rel = self.rel
                quote_type = self.ch
                self.next()

                s = ""
                while True:
                    assert self.ch not in "\r\n", "unterminated string"
                    if self.ch == quote_type:
                        self.next()
                        break
                    s += self.ch
                    self.next()
                self.token(TokenType.STR, s, rel=rel)
            else:
                assert False, f"invalid char '{self.ch}'"
        return self.tokens

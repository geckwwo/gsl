from lang.front.lexer import Token, TokenType, Keyword
from lang.front.nodes import *

class CmpToBinOp:
    EQ = BinOp.EQ
    NEQ = BinOp.NEQ
    LT = BinOp.LT
    LTE = BinOp.LTE
    GT = BinOp.GT
    GTE = BinOp.GTE
class P1ToBinOp:
    PLUS = BinOp.ADD
    MINUS = BinOp.SUB
class P2ToBinOp:
    MUL = BinOp.MUL
    DIV = BinOp.DIV
    MOD = BinOp.MOD
class Parser:
    def __reset(self, tokens):
        self.tokens = tokens
        self.tok = None
        self.idx = -1

    def next(self, step=1):
        self.idx += step
        self.tok = self.tokens[self.idx] if self.idx < len(self.tokens) else None

    def run(self, tokens):
        self.__reset(tokens)
        self.next()
        body = []
        while self.tok is not None:
            body.append(self.stmt())
        return body
    
    def stmt(self):
        if self.tok.type == TokenType.KEYWORD:
            if self.tok.value == Keyword.IF:
                return self.if_stmt()
            elif self.tok.value == Keyword.WHILE:
                return self.while_stmt()
            elif self.tok.value == Keyword.FUN:
                return self.func()
            elif self.tok.value == Keyword.FOR:
                return self.for_stmt()
            elif self.tok.value == Keyword.FOREACH:
                return self.foreach_stmt()
            elif self.tok.value == Keyword.RETURN:
                self.next()
                val = self.expr() if self.tok.type != TokenType.SEMICOLON else None
                assert self.tok.type == TokenType.SEMICOLON, "semicolon expected"
                self.next()
                return NodeReturn(val)
            elif self.tok.value == Keyword.BREAK:
                self.next()
                assert self.tok.type == TokenType.SEMICOLON, "semicolon expected"
                self.next()
                return NodeBreak()
            else:
                assert False, f"keyword '{self.tok.value}' is not implemented"
        else:
            e = self.expr()
            if self.tok.type == TokenType.ASSIGN:
                self.next()
                assert isinstance(e, (NodeIden,)), f"cannot assign to {e}"
                e = NodeAssign(e, self.expr())
                assert self.tok.type == TokenType.SEMICOLON, "semicolon expected"
                self.next()
                return e
            assert self.tok.type == TokenType.SEMICOLON, "semicolon expected"
            self.next()

            return NodeDiscard(e)

    def for_stmt(self):
        assert self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.FOR, "'for' expected"
        self.next()
        
        assert self.tok.type == TokenType.LPAR, "'(' expected"
        self.next()

        assert self.tok.type == TokenType.IDEN, "identifier expected"
        initname = self.tok.value
        self.next()

        assert self.tok.type == TokenType.ASSIGN, "'=' expected"
        self.next()

        initval = self.expr()

        assert self.tok.type == TokenType.COMMA, "',' expected"
        self.next()

        endval = self.expr()

        assert self.tok.type == TokenType.RPAR, "')' expected"
        self.next()

        assert self.tok.type == TokenType.LCUR, "'{' expected"
        self.next()
        
        body = []
        while self.tok.type != TokenType.RCUR:
            body.append(self.stmt())
        self.next()
        return NodeFor(initname, initval, endval, body)
    
    def foreach_stmt(self):
        assert self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.FOREACH, "'foreach' expected"
        self.next()
        
        assert self.tok.type == TokenType.LPAR, "'(' expected"
        self.next()

        assert self.tok.type == TokenType.IDEN, "identifier expected"
        initname = self.tok.value
        self.next()

        assert self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.IN, "'in' expected"
        self.next()

        endval = self.expr()

        assert self.tok.type == TokenType.RPAR, "')' expected"
        self.next()

        assert self.tok.type == TokenType.LCUR, "'{' expected"
        self.next()
        
        body = []
        while self.tok.type != TokenType.RCUR:
            body.append(self.stmt())
        self.next()
        return NodeForeach(initname, endval, body)

    def func(self):
        assert self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.FUN, "'fun' expected"
        self.next()
        
        assert self.tok.type in (TokenType.LPAR, TokenType.IDEN), "'(' or identifier expected"
        name = None
        if self.tok.type == TokenType.IDEN:
            name = self.tok.value
            self.next()
            assert self.tok.type == TokenType.LPAR, "'(' expected"
        self.next()
        args = []
        while True:
            if self.tok.type == TokenType.RPAR:
                self.next()
                break
            assert self.tok.type == TokenType.IDEN, "identifier expected"
            args.append(self.tok.value)
            self.next()
            assert self.tok.type in (TokenType.COMMA, TokenType.RPAR), "',' or ')' expected"
            if self.tok.type == TokenType.RPAR:
                self.next()
                break
            else:
                self.next()
        
        assert self.tok.type == TokenType.LCUR, "'{' expected"
        self.next()

        body = []
        while self.tok.type != TokenType.RCUR:
            body.append(self.stmt())
        self.next()
        return NodeFunction(name, args, body)
    
    def while_stmt(self):
        assert self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.WHILE, "'while' expected"
        self.next()

        assert self.tok.type == TokenType.LPAR, "'(' expected"
        self.next()

        cond = self.expr()

        assert self.tok.type == TokenType.RPAR, "')' expected"
        self.next()

        assert self.tok.type == TokenType.LCUR, "'{' expected"
        self.next()

        body = []
        while self.tok.type != TokenType.RCUR:
            body.append(self.stmt())
        self.next()
        
        return NodeWhile(cond, body)

    def if_stmt(self):
        assert self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.IF, "'if' expected"
        self.next()

        assert self.tok.type == TokenType.LPAR, "'(' expected"
        self.next()

        cond = self.expr()

        assert self.tok.type == TokenType.RPAR, "')' expected"
        self.next()

        assert self.tok.type == TokenType.LCUR, "'{' expected"
        self.next()

        body = []
        while self.tok.type != TokenType.RCUR:
            body.append(self.stmt())
        self.next()
        
        elseifs = []
        while self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.ELSEIF:
            self.next()

            assert self.tok.type == TokenType.LPAR, "'(' expected"
            self.next()

            cond2 = self.expr()

            assert self.tok.type == TokenType.RPAR, "')' expected"
            self.next()

            assert self.tok.type == TokenType.LCUR, "'{' expected"
            self.next()

            body2 = []
            while self.tok.type != TokenType.RCUR:
                body2.append(self.stmt())
            self.next()
            elseifs.append((cond2,body2))
        
        else_ = []
        if self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.ELSE:
            self.next()

            assert self.tok.type == TokenType.LCUR, "'{' expected"
            self.next()

            while self.tok.type != TokenType.RCUR:
                else_.append(self.stmt())
            self.next()
        return NodeIf(cond, body, elseifs, else_)
    
    def expr(self):
        """
        Priority
        Bottom 1 == != >= > <= <
        |      2 + -
        |      3 * /
        |      4 (?)
        |      5 (?)
        |      6 (?)
        Top    7 [] . call
               8 () atom
        """
        left = self.expr2()
        while self.tok.type.name in dir(CmpToBinOp):
            op = getattr(CmpToBinOp,self.tok.type.name)
            self.next()
            right = self.expr()
            left = NodeBinOp(left,op,right)
        return left
    def expr2(self):
        left = self.expr3()
        while self.tok.type.name in dir(P1ToBinOp):
            op = getattr(P1ToBinOp,self.tok.type.name)
            self.next()
            right = self.expr()
            left = NodeBinOp(left,op,right)
        return left
    def expr3(self):
        left = self.expr7()
        while self.tok.type.name in dir(P2ToBinOp):
            op = getattr(P2ToBinOp,self.tok.type.name)
            self.next()
            right = self.expr()
            left = NodeBinOp(left,op,right)
        return left
    def expr7(self):
        left = self.expr8()
        while self.tok.type in (TokenType.DOT, TokenType.LPAR, TokenType.LBRK):
            if self.tok.type == TokenType.DOT:
                self.next()
                assert self.tok.type == TokenType.IDEN, "identifier expected"
                left = NodeAttr(left, self.tok.value)
                self.next()
            
            elif self.tok.type == TokenType.LBRK:
                self.next()
                index = self.expr()
                assert self.tok.type == TokenType.RBRK, "']' expected"
                self.next()
                left = NodeIndex(left, index)
            elif self.tok.type == TokenType.LPAR:
                self.next()
                args = []
                while True:
                    if self.tok.type == TokenType.RPAR:
                        self.next()
                        break
                    args.append(self.expr())
                    assert self.tok.type in (TokenType.RPAR, TokenType.COMMA), "',' or ')' expected"
                    if self.tok.type == TokenType.RPAR:
                        self.next()
                        break
                    else:
                        self.next()
                left = NodeCall(left, args)
            else:
                raise NotImplementedError(f"expr7 {self.tok}")
        return left
    def expr8(self):
        if self.tok.type in (TokenType.INT, TokenType.FLOAT, TokenType.STR):
            v = self.tok.value
            self.next()
            return NodeConst(v)
        elif self.tok.type == TokenType.IDEN:
            v = self.tok.value
            self.next()
            return NodeIden(v)
        elif self.tok.type == TokenType.LPAR:
            self.next()
            v = self.expr()
            assert self.tok.type == TokenType.RPAR, "')' expected"
            self.next()
            return v
        elif self.tok.type == TokenType.LBRK:
            self.next()
            args = []
            while True:
                if self.tok.type == TokenType.RBRK:
                    self.next()
                    break
                args.append(self.expr())
                assert self.tok.type in (TokenType.RBRK, TokenType.COMMA), "',' or ']' expected"
                if self.tok.type == TokenType.RBRK:
                    self.next()
                    break
                else:
                    self.next()
            return NodeList(args)
        elif self.tok.type == TokenType.KEYWORD and self.tok.value == Keyword.FUN:
            return self.func()
        elif self.tok.type == TokenType.NOT:
            self.next()
            return NodeUnaryOp(UnaryOp.NOT, self.expr())
        else:
            raise NotImplementedError(f"atom {self.tok} err")
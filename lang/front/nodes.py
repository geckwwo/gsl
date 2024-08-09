import enum

class Node:
    def __repr__(self):
        kw = filter(lambda x: not (x.startswith("__") and x.endswith("__")), dir(self))
        kwe = map(lambda x: f"{x}={repr(getattr(self,x))}", kw)
        return f"{self.__class__.__name__}({', '.join(kwe)})"

class NodeAssign(Node):
    def __init__(self, exprleft, exprright):
        self.exprleft = exprleft
        self.exprright = exprright

class NodeIden(Node):
    def __init__(self, iden):
        self.iden = iden

class NodeConst(Node):
    def __init__(self, value):
        self.value = value
class NodeList(Node):
    def __init__(self, value):
        self.value = value

class NodeAttr(Node):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr
class NodeIndex(Node):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

class NodeIf(Node):
    def __init__(self, cond, body, elseifs, else_):
        self.cond = cond
        self.body = body
        self.elseifs = elseifs
        self.else_ = else_

class NodeWhile(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
class NodeBreak(Node):
    def __init__(self):
        pass

class NodeCall(Node):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class NodeFunction(Node):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

class NodeFor(Node):
    def __init__(self, initname, initval, endval, body):
        self.initname = initname
        self.initval = initval
        self.endval = endval
        self.body = body

class NodeForeach(Node):
    def __init__(self, initname, iterator, body):
        self.initname = initname
        self.iterator = iterator
        self.body = body


class NodeDiscard(Node):
    def __init__(self, expr):
        self.expr = expr

class NodeReturn(Node):
    def __init__(self, value):
        self.value = value

class BinOp(enum.Enum):
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    MOD = 5

    EQ = 10
    NEQ = 11
    LT = 12
    LTE = 13
    GT = 14
    GTE = 15
    NOT = 16

    LOGAND = 20
    LOGOR = 21
    LOGXOR = 22

    AND = 30
    OR = 31
    XOR = 32

class NodeBinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

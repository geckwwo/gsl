from lang.front.nodes import *

class IRComponent:
    def __repr__(self):
        kw = filter(lambda x: not (x.startswith("__") and x.endswith("__")), dir(self))
        kwe = map(lambda x: f"{x}={repr(getattr(self,x))}", kw)
        return f"{self.__class__.__name__}({', '.join(kwe)})"

class IRFunction(IRComponent):
    def __init__(self, name, args, body, locals=None):
        self.name = name
        self.args = args
        self.body = body
        self.locals = locals if locals is not None else []

class IRCall(IRComponent):
    def __init__(self, called, args):
        self.called = called
        self.args = args

class IRIden(IRComponent):
    def __init__(self, iden):
        self.iden = iden

class IRConst(IRComponent):
    def __init__(self, value):
        self.value = value
class IRDiscard(IRComponent):
    def __init__(self, value):
        self.value = value
class IRReturn(IRComponent):
    def __init__(self, value):
        self.value = value
class IRIf(IRComponent):
    def __init__(self, cond, if_, elseifs, else_):
        self.cond = cond
        self.if_ = if_
        self.elseifs = elseifs
        self.else_ = else_

class IRB_Compare(IRComponent):
    def __init__(self, left, right):
        self.left = left
        self.right = right
class IRB_Divide(IRComponent):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class IRGenerator:
    def __init__(self):
        self.__func_local_stack = []
    def visit(self, node: Node):
        return getattr(self, "visit_" + node.__class__.__name__)(node)
    def run(self, ast: list[Node]):
        b = []
        self.__func_local_stack.append([])
        for node in ast:
            b.append(self.visit(node))
        return IRFunction("__gslmain__", [], b, self.__func_local_stack.pop())
    def visit_NodeCall(self, node: NodeCall):
        return IRCall(self.visit(node.callee), list(map(self.visit, node.args)))
    def visit_NodeIden(self, node: NodeIden):
        return IRIden(node.iden)
    def visit_NodeConst(self, node: NodeConst):
        return IRConst(node.value)
    def visit_NodeDiscard(self, node: NodeDiscard):
        return IRDiscard(self.visit(node.expr))
    def visit_NodeFunction(self, node: NodeFunction):
        self.__func_local_stack.append([])
        pbody = list(map(self.visit, node.body))
        return IRFunction(node.name, node.args, pbody, self.__func_local_stack.pop())
    def visit_NodeIf(self, node: NodeIf):
        # man whatever just get this working
        return IRIf(self.visit(node.cond), list(map(self.visit, node.body)), list(map(lambda cond, body: (self.visit(cond), list(map(self.visit, body))), node.elseifs)), list(map(self.visit, node.else_)) if node.else_ is not None else None)
    def visit_NodeBinOp(self, node: NodeBinOp):
        return {
            BinOp.EQ: IRB_Compare,
            BinOp.DIV: IRB_Divide
        }[node.op](self.visit(node.left), self.visit(node.right))
    def visit_NodeReturn(self, node: NodeReturn):
        return IRReturn(self.visit(node.value) if node.value is not None else None)
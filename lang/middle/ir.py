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
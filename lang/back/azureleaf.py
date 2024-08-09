from lang.middle.ir import *

class ALComponent:
    def __repr__(self):
        kw = filter(lambda x: not (x.startswith("__") and x.endswith("__")), dir(self))
        kwe = map(lambda x: f"{x}={repr(getattr(self,x))}", kw)
        return f"{self.__class__.__name__}({', '.join(kwe)})"

class ALFunction(ALComponent):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

class ALInvoke(ALComponent):
    def __init__(self, amount):
        self.amount = amount

class ALDrop(ALComponent):
    pass

class ALPushConst(ALComponent):
    def __init__(self, value):
        self.value = value
class ALGet(ALComponent):
    pass

def flatmap(func, x):
    result = []
    for i in x:
        result.extend(func(i))
    return result

class AzureLeafCompiler:
    def __init__(self):
        self.__cfun_locals = []
    def visit(self, ic: IRComponent):
        return getattr(self, "visit_" + ic.__class__.__name__)(ic)
    def visit_IRFunction(self, ic: IRFunction):
        self.__cfun_locals.append(ic.locals)
        f = ALFunction(ic.name, ic.args, flatmap(self.visit, ic.body))
        self.__cfun_locals.pop()
        return f
    def visit_IRCall(self, ic: IRCall):
        v = []
        v.extend(flatmap(self.visit, ic.args))
        v.extend(self.visit(ic.called))
        v.append(ALInvoke(len(ic.args)))
        return v
    def visit_IRDiscard(self, ic: IRDiscard):
        x = self.visit(ic.value)
        x.append(ALDrop())
        return x
    def visit_IRConst(self, ic: IRConst):
        return [ALPushConst(ic.value)]
    def visit_IRIden(self, ic: IRIden):
        return [ALPushConst(ic.iden), ALGet()]
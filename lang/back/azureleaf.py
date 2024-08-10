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
class ALPushBody(ALComponent):
    def __init__(self, value):
        self.value = value
class ALGet(ALComponent):
    pass
class ALCompare(ALComponent):
    pass
class ALDivide(ALComponent):
    pass
class ALReturn(ALComponent):
    pass
class ALNothing(ALComponent):
    pass

class ALJumpRelative(ALComponent):
    def __init__(self, amt):
        self.amt = amt
class ALJumpTrueRelative(ALComponent):
    def __init__(self, amt):
        self.amt = amt
class ALJumpFalseRelative(ALComponent):
    def __init__(self, amt):
        self.amt = amt

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
        # TODO what the fuck is this
        return [ALPushBody(f.body), *[ALPushConst(x) for x in ic.args], ALPushConst("__gsl_hacks_listargs"), ALGet(), ALInvoke(len(ic.args)), ALPushConst(f.name), ALPushConst("__gsl_hacks_buildfunc"), ALGet(), ALInvoke(3)]
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
    def run(self, ic: IRFunction):
        self.__cfun_locals.append(ic.locals)
        f = ALFunction(ic.name, ic.args, flatmap(self.visit, ic.body))
        self.__cfun_locals.pop()
        return f
    def visit_IRIf(self, ic: IRIf):
        assert len(ic.elseifs) == 0, "elseif is not supported right now by azure leaf compiler"
        v = self.visit(ic.cond)
        c = flatmap(self.visit, ic.if_)
        if len(ic.else_) == 0:
            v.extend([ALJumpFalseRelative(len(c)), *c])
        else:
            elsec = flatmap(self.visit, ic.else_)
            v.extend([ALJumpFalseRelative(len(c)+1), *c, ALJumpRelative(len(elsec)), *elsec])
        return v
    def visit_IRB_Compare(self, ic: IRB_Compare):
        return [*self.visit(ic.left), *self.visit(ic.right), ALCompare()]
    def visit_IRB_Divide(self, ic: IRB_Divide):
        return [*self.visit(ic.left), *self.visit(ic.right), ALDivide()]
    def visit_IRReturn(self, ic: IRReturn):
        return [*(self.visit(ic.value) if ic.value is not None else (ALNothing(),)), ALReturn()]
from lang.back.azureleaf import *

class AzureLeafScopedExecutionContextTemplate:
    def __init__(self, name, args, body, parent_ctx):
        self.name = name
        self.args = args
        self.body = body
        self.parent_ctx = parent_ctx
    def __call__(self, ctx, executor, *args):
        vx = AzureLeafScopedExecutionContext(self.name, self.body, self.parent_ctx)
        executor.push_context(vx, self.args, args)

SENTINEL = object()

class AzureLeafScopedExecutionContext:
    def __init__(self, name, code, parent_ctx=None):
        self.name = name
        self.code = code
        self.parent_ctx = parent_ctx

        self.pc = 0
        self.stack = []
        def x__gsl_hacks_buildfunc(ctx, executor, body, args, name):
            self.locals[name] = AzureLeafScopedExecutionContextTemplate(name, args, body, ctx)
        def x__gsl_iter_get(ctx, executor, thing):
            try:
                return next(thing)
            except StopIteration:
                return SENTINEL
        self.locals = {
            "__gsl_hacks_listargs": lambda c,e,*a: a,
            "__gsl_hacks_buildfunc": x__gsl_hacks_buildfunc,
            "__gsl_iter": lambda c,e,x: iter(x),
            "__gsl_iter_get": x__gsl_iter_get,
            "__gsl_iter_get_sentinel": lambda c,e: SENTINEL,
            "contains": lambda c,e,a,b: b in a,
            "append": lambda c,e,a,b: a.append(b),
            "filterlist": lambda c,e,a,b: list(filter(a, b)),
            "range": lambda c,e,*x: range(*x)
        }
    def tick(self, executor):
        if self.pc >= len(self.code):
            return False
        i = self.code[self.pc]
        #print(self.pc, i)
        self.pc += 1
        if isinstance(i, ALPushConst):
            self.stack.append(i.value)
        elif isinstance(i, ALGet):
            name = self.stack.pop()
            self.stack.append(self.getval(name, executor))
        elif isinstance(i, ALDrop):
            self.stack.pop()
        elif isinstance(i, ALDupe):
            self.stack.append(self.stack[-1])
        elif isinstance(i, ALInvoke):
            called = self.stack.pop()
            args = (self.stack.pop() for _ in range(i.amount))
            self.stack.append(called(self,executor,*reversed(list(args))))
        elif isinstance(i, ALPushBody):
            self.stack.append(i.value)
        elif isinstance(i, ALCompare):
            self.stack.append(self.stack.pop() == self.stack.pop())
        elif isinstance(i, ALDivide):
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a / b)
        elif isinstance(i, ALAdd):
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)
        elif isinstance(i, ALMultiply):
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)
        elif isinstance(i, ALNot):
            self.stack.append(not self.stack.pop())
        elif isinstance(i, ALJumpFalseRelative):
            if not self.stack.pop():
                self.pc += i.amt
        elif isinstance(i, ALJumpTrueRelative):
            if self.stack.pop():
                self.pc += i.amt
        elif isinstance(i, ALJumpRelative):
            self.pc += i.amt
        elif isinstance(i, ALGetAttribute):
            obj, attr = self.stack.pop(), self.stack.pop()
            self.stack.append(getattr(obj, attr))
        elif isinstance(i, ALReturn):
            rv = self.stack.pop()
            executor.ctx_stack[-2].stack.append(rv)
            return False
        elif isinstance(i, ALNothing):
            self.stack.append(None)
        elif isinstance(i, ALPutLocal):
            name, value = self.stack.pop(), self.stack.pop()
            self.locals[name] = value
        else:
            raise NotImplementedError(f"Opcode not implemented {i}")
        return True
    
    def getval(self, name, executor):
        if name in self.locals:
            return self.locals[name]
        if name in executor.global_ctx:
            return executor.global_ctx[name]
        if self.parent_ctx:
            return self.parent_ctx.getval(name, executor)
        raise NameError(f"cannot find variable {name}")

class AzureLeafExecutor:
    def __init__(self, global_ctx):
        self.ctx_stack = []
        self.global_ctx = global_ctx
    def tick(self):
        if not self.ctx_stack[-1].tick(self):
            self.ctx_stack.pop()
        return len(self.ctx_stack) > 0
    def push_context(self, context, argnames, args):
        assert len(argnames) == len(args), f"fn expected {len(argnames)} args, got {len(args)}"
        for argname, arg in zip(argnames, args):
            context.locals[argname] = arg
        self.ctx_stack.append(context)
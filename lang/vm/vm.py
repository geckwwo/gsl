from lang.back.azureleaf import *


class AzureLeafDataContext:
    pass

class AzureLeafScopedExecutionContext:
    def __init__(self, name, code, parent_ctx=None):
        self.name = name
        self.code = code
        self.parent_ctx = parent_ctx

        self.pc = 0
        self.stack = []
        self.locals = {}
    def tick(self, executor):
        if self.pc >= len(self.code):
            return False
        i = self.code[self.pc]
        self.pc += 1
        if isinstance(i, ALPushConst):
            self.stack.append(i.value)
        elif isinstance(i, ALGet):
            name = self.stack.pop()
            self.stack.append(self.getval(name, executor))
        elif isinstance(i, ALDrop):
            self.stack.pop()
        elif isinstance(i, ALInvoke):
            called = self.stack.pop()
            args = (self.stack.pop() for _ in range(i.amount))
            self.stack.append(called(self,executor,*reversed(list(args))))
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
from front.nodes import *

class LuaTranspiler:
    def run(self, ast: list[Node]):
        f = "-- GSL codegen\n-- !! Autogenerated !! Do not edit, your changes will be overwritten !!\n\n"
        for i in ast:
            f += self.visit(i, 0) + "\n"
        return f
    def visit(self, node: Node, tabs):
        return getattr(self, "visit_" + node.__class__.__name__)(node, tabs)
    def visit_NodeCall(self, node: NodeCall, tabs):
        return ("\t"*tabs) + f"{self.visit(node.callee, 0)}({', '.join(map(lambda x: self.visit(x, 0), node.args))})"
    def visit_NodeConst(self, node: NodeConst, tabs):
        return ("\t"*tabs) + repr(node.value)
    def visit_NodeIden(self, node: NodeIden, tabs):
        return ("\t"*tabs) + node.iden
    def visit_NodeAssign(self, node: NodeAssign, tabs):
        if isinstance(node.exprleft, NodeIden):
            return ("\t"*tabs) + f"local {self.visit(node.exprleft,0)} = {self.visit(node.exprright,0)}"
        else:
            return ("\t"*tabs) + f"{self.visit(node.exprleft,0)} = {self.visit(node.exprright,0)}"
    def visit_NodeIf(self, node: NodeIf, tabs):
        code = ("\t"*tabs) + f"if {self.visit(node.cond,0)} then\n"
        code += "\n".join(map(lambda x: self.visit(x, tabs+1), node.body)) + "\n"
        for i in node.elseifs:
            code += ("\t"*tabs) + f"elseif {self.visit(i[0],0)} then\n"
            code += "\n".join(map(lambda x: self.visit(x, tabs+1), i[1])) + "\n"
        if len(node.else_) > 0:
            code += "else\n"
            code += "\n".join(map(lambda x: self.visit(x, tabs+1), node.else_)) + "\n"
        code += "end"
        return code
    def visit_NodeBinOp(self, node: NodeBinOp, tabs):
        op = {
            BinOp.ADD: "+",
            BinOp.MUL: "*",
            BinOp.EQ: "=="
        }[node.op]
        return ("\t"*tabs) + f"{self.visit(node.left, 0)} {op} {self.visit(node.right, 0)}"
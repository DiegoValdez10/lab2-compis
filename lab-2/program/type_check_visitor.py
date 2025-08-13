from SimpleLangParser import SimpleLangParser
from SimpleLangVisitor import SimpleLangVisitor
from custom_types import IntType, FloatType, StringType, BoolType

NUM_TYPES = (IntType, FloatType)

def promote_numeric(l, r):
    return FloatType() if isinstance(l, FloatType) or isinstance(r, FloatType) else IntType()

class TypeCheckVisitor(SimpleLangVisitor):
    def __init__(self):
        self.errors = []

    def visitInt(self, ctx: SimpleLangParser.IntContext):
        return IntType()

    def visitFloat(self, ctx: SimpleLangParser.FloatContext):
        return FloatType()

    def visitString(self, ctx: SimpleLangParser.StringContext):
        return StringType()

    def visitBool(self, ctx: SimpleLangParser.BoolContext):
        return BoolType()

    def visitParens(self, ctx: SimpleLangParser.ParensContext):
        return self.visit(ctx.expr())


    def visitPow(self, ctx: SimpleLangParser.PowContext):
        l = self.visit(ctx.expr(0))
        r = self.visit(ctx.expr(1))
        if isinstance(l, NUM_TYPES) and isinstance(r, NUM_TYPES):
            return promote_numeric(l, r)
        self.errors.append(f"[{ctx.start.line}:{ctx.start.column}] Unsupported operand types for ^: {l} and {r}")
        return None

    def visitMulDiv(self, ctx: SimpleLangParser.MulDivContext):
        l = self.visit(ctx.expr(0))
        r = self.visit(ctx.expr(1))
        op = ctx.op.text

        if op == '%':
            if isinstance(l, IntType) and isinstance(r, IntType):
                return IntType()
            self.errors.append(f"[{ctx.start.line}:{ctx.start.column}] Modulo (%) only supports int % int, got {l} % {r}")
            return None

        if isinstance(l, NUM_TYPES) and isinstance(r, NUM_TYPES):
            try:
                if op == '/' and ctx.expr(1).getText() == '0':
                    self.errors.append(f"[{ctx.start.line}:{ctx.start.column}] Division by zero")
                    return None
            except AttributeError:
                pass
            return FloatType() if op == '/' or isinstance(l, FloatType) or isinstance(r, FloatType) else IntType()

        self.errors.append(f"[{ctx.start.line}:{ctx.start.column}] Unsupported operand types for {op}: {l} and {r}")
        return None

    def visitAddSub(self, ctx: SimpleLangParser.AddSubContext):
        l = self.visit(ctx.expr(0))
        r = self.visit(ctx.expr(1))
        op = ctx.op.text
        print("DEBUG AddSub:", l, type(l), r, type(r))
        if op == '+':
            if isinstance(l, NUM_TYPES) and isinstance(r, NUM_TYPES):
                return promote_numeric(l, r)
            if isinstance(l, StringType) and isinstance(r, StringType):
                return StringType()
            self.errors.append(f"[{ctx.start.line}:{ctx.start.column}] Unsupported operand types for +: {l} and {r}")
            return None

        if isinstance(l, NUM_TYPES) and isinstance(r, NUM_TYPES):
            return promote_numeric(l, r)

        self.errors.append(f"[{ctx.start.line}:{ctx.start.column}] Unsupported operand types for -: {l} and {r}")
        return None

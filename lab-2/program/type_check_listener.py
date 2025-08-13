from SimpleLangListener import SimpleLangListener
from SimpleLangParser import SimpleLangParser
from custom_types import IntType, FloatType, StringType, BoolType

NUM_TYPES = (IntType, FloatType)

def promote_numeric(l, r):
    return FloatType() if isinstance(l, FloatType) or isinstance(r, FloatType) else IntType()

class TypeCheckListener(SimpleLangListener):

  def __init__(self):
    self.errors = []
    self.types = {}

  # --------- Utilidad para mensajes con línea/col ---------
  def _err(self, ctx, msg):
    ln = getattr(getattr(ctx, "start", None), "line", -1)
    col = getattr(getattr(ctx, "start", None), "column", -1)
    self.errors.append(f"[{ln}:{col}] {msg}")

  # --------- Literales ---------
  def enterInt(self, ctx: SimpleLangParser.IntContext):
    self.types[ctx] = IntType()

  def enterFloat(self, ctx: SimpleLangParser.FloatContext):
    self.types[ctx] = FloatType()

  def enterString(self, ctx: SimpleLangParser.StringContext):
    self.types[ctx] = StringType()

  def enterBool(self, ctx: SimpleLangParser.BoolContext):
    self.types[ctx] = BoolType()

  # --------- Paréntesis ---------
  def exitParens(self, ctx: SimpleLangParser.ParensContext):
    self.types[ctx] = self.types[ctx.expr()]

  # --------- Potencia: a ^ b (num ^ num) ---------
  def exitPow(self, ctx: SimpleLangParser.PowContext):
    l = self.types[ctx.expr(0)]
    r = self.types[ctx.expr(1)]
    if isinstance(l, NUM_TYPES) and isinstance(r, NUM_TYPES):
      self.types[ctx] = promote_numeric(l, r)
    else:
      self._err(ctx, f"Unsupported operand types for ^: {l} and {r}")
      self.types[ctx] = FloatType()

  # --------- *, /, % ---------
  def exitMulDiv(self, ctx: SimpleLangParser.MulDivContext):
    l = self.types[ctx.expr(0)]
    r = self.types[ctx.expr(1)]
    op = ctx.op.text

    if op == '%':
      # % solo entre enteros
      if isinstance(l, IntType) and isinstance(r, IntType):
        self.types[ctx] = IntType()
      else:
        self._err(ctx, f"Modulo (%) only supports int % int, got {l} % {r}")
        self.types[ctx] = IntType()
      return

    # * o /
    if isinstance(l, NUM_TYPES) and isinstance(r, NUM_TYPES):
      # división por cero si RHS es literal 0
      try:
        rhs_txt = ctx.expr(1).getText()
        if op == '/' and rhs_txt == '0':
          self._err(ctx, "Division by zero")
      except Exception:
        pass

      self.types[ctx] = FloatType() if op == '/' or isinstance(l, FloatType) or isinstance(r, FloatType) \
                        else IntType()
    else:
      self._err(ctx, f"Unsupported operand types for {op}: {l} and {r}")
      self.types[ctx] = FloatType()

  # --------- +, - ---------
  def exitAddSub(self, ctx: SimpleLangParser.AddSubContext):
    l = self.types[ctx.expr(0)]
    r = self.types[ctx.expr(1)]
    op = ctx.op.text

    if op == '+':
      # num + num
      if isinstance(l, NUM_TYPES) and isinstance(r, NUM_TYPES):
        self.types[ctx] = promote_numeric(l, r)
      # string + string
      elif isinstance(l, StringType) and isinstance(r, StringType):
        self.types[ctx] = StringType()
      else:
        self._err(ctx, f"Unsupported operand types for +: {l} and {r}")
        self.types[ctx] = StringType()
    else:  # '-'
      if isinstance(l, NUM_TYPES) and isinstance(r, NUM_TYPES):
        self.types[ctx] = promote_numeric(l, r)
      else:
        self._err(ctx, f"Unsupported operand types for -: {l} and {r}")
        self.types[ctx] = FloatType()

import re
import ast
import operator
import math

# Diccionario seguro de operaciones permitidas
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.BitXor: operator.xor,
    ast.FloorDiv: operator.floordiv,
}

# Funciones matemáticas seguras permitidas
SAFE_FUNCTIONS = {
    'abs': abs,
    'min': min,
    'max': max,
    'round': round,
    'math.sqrt': math.sqrt,
    'math.sin': math.sin,
    'math.cos': math.cos,
    'math.tan': math.tan,
    'math.log': math.log,
    'math.log10': math.log10,
    'math.exp': math.exp,
    'math.pi': math.pi,
    'math.e': math.e,
}

class SafeEvaluator(ast.NodeVisitor):
    def __init__(self):
        self.stack = []

    def visit_Num(self, node):
        self.stack.append(node.n)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id in SAFE_FUNCTIONS:
                self.stack.append(SAFE_FUNCTIONS[node.id])
            else:
                raise ValueError(f"Nombre no permitido: {node.id}")

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        right = self.stack.pop()
        left = self.stack.pop()
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Operador no permitido: {type(node.op).__name__}")
        self.stack.append(op(left, right))

    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        operand = self.stack.pop()
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Operador unario no permitido: {type(node.op).__name__}")
        self.stack.append(op(operand))

    def visit_Call(self, node):
        self.visit(node.func)
        func = self.stack.pop()
        args = []
        for arg in node.args:
            self.visit(arg)
            args.append(self.stack.pop())
        if func not in SAFE_FUNCTIONS.values():
            raise ValueError(f"Función no permitida: {func}")
        self.stack.append(func(*args))

    def evaluate(self, node):
        self.visit(node)
        if len(self.stack) != 1:
            raise ValueError("Expresión inválida")
        return self.stack[0]

def safe_eval(expr):
    # Validar caracteres permitidos
    if not re.match(r'^[\d+\-*/()., \t\n\r\w]+$', expr):
        raise ValueError("Caracteres no permitidos en la expresión")

    # Parsear el AST
    try:
        node = ast.parse(expr, mode='eval')
    except SyntaxError as e:
        raise ValueError(f"Error de sintaxis: {e}")

    # Evaluar de forma segura
    evaluator = SafeEvaluator()
    return evaluator.evaluate(node.body)

def main():
    print("Calculadora segura. Escribe 'salir' para terminar.")
    while True:
        try:
            expr = input("> ").strip()
            if expr.lower() in ('salir', 'exit', 'quit'):
                break

            if not expr:
                continue

            result = safe_eval(expr)
            print(f"Resultado: {result}")

        except ValueError as e:
            print(f"Error: {e}")
        except ZeroDivisionError:
            print("Error: División por cero")
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()

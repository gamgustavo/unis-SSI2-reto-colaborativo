import ast
import operator
import math
import sys

class SafeCalculator:
    """Calculadora segura que evalúa expresiones matemáticas con restricciones."""
    
    # Operadores seguros permitidos
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }
    
    # Funciones matemáticas seguras permitidas
    SAFE_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'pi': math.pi,
        'e': math.e,
        'radians': math.radians,
        'degrees': math.degrees,
    }
    
    # Constantes seguras
    SAFE_CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
    }
    
    def __init__(self):
        self.allowed_nodes = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Constant,
            ast.Name,
            ast.Call,
            ast.Load,
        )
    
    def is_safe(self, node):
        """Verifica si un nodo AST es seguro para evaluar."""
        if not isinstance(node, self.allowed_nodes):
            raise ValueError(f"Tipo de nodo no permitido: {type(node).__name__}")
        
        if isinstance(node, ast.Call):
            # Verificar que la función llamada sea segura
            if not isinstance(node.func, ast.Name):
                raise ValueError("Llamadas a funciones complejas no permitidas")
            
            func_name = node.func.id
            if func_name not in self.SAFE_FUNCTIONS:
                raise ValueError(f"Función no permitida: {func_name}")
            
            # Verificar argumentos recursivamente
            for arg in node.args:
                self.is_safe(arg)
                
        elif isinstance(node, ast.Name):
            # Verificar que el nombre sea una constante segura
            if node.id not in self.SAFE_CONSTANTS:
                raise ValueError(f"Nombre no permitido: {node.id}")
                
        elif isinstance(node, ast.BinOp):
            # Verificar que el operador sea seguro
            if type(node.op) not in self.SAFE_OPERATORS:
                raise ValueError(f"Operador no permitido: {type(node.op).__name__}")
            
            # Verificar operandos recursivamente
            self.is_safe(node.left)
            self.is_safe(node.right)
            
        elif isinstance(node, ast.UnaryOp):
            # Verificar que el operador unario sea seguro
            if type(node.op) not in self.SAFE_OPERATORS:
                raise ValueError(f"Operador unario no permitido: {type(node.op).__name__}")
            
            # Verificar operando recursivamente
            self.is_safe(node.operand)
            
        elif isinstance(node, ast.Constant):
            # Verificar que el valor sea numérico
            if not isinstance(node.value, (int, float)):
                raise ValueError(f"Tipo de constante no permitido: {type(node.value).__name__}")
        
        return True
    
    def evaluate(self, expr):
        """Evalúa una expresión matemática de forma segura."""
        try:
            # Parsear la expresión en AST
            tree = ast.parse(expr, mode='eval')
            
            # Verificar seguridad del AST
            self.is_safe(tree.body)
            
            # Compilar y evaluar de forma segura
            code = compile(tree, '<string>', 'eval')
            
            # Crear entorno seguro para evaluación
            safe_env = {
                **self.SAFE_FUNCTIONS,
                **self.SAFE_CONSTANTS,
                '__builtins__': {}  # Bloquear builtins inseguros
            }
            
            result = eval(code, safe_env, {})
            
            # Verificar que el resultado sea finito
            if not math.isfinite(result):
                raise ValueError("Resultado no finito (infinito o NaN)")
                
            return result
            
        except SyntaxError:
            raise ValueError("Expresión con sintaxis inválida")
        except ZeroDivisionError:
            raise ValueError("División por cero")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error al evaluar la expresión: {str(e)}")

def main():
    """Función principal de la calculadora."""
    calculator = SafeCalculator()
    
    print("Calculadora Segura")
    print("=" * 50)
    print("Operadores: + - * / ** // %")
    print("Funciones: abs, round, min, max, sqrt, sin, cos, tan, log, log10, exp")
    print("Constantes: pi, e")
    print("Ejemplos: 2 + 3 * 4, sin(pi/2), sqrt(16)")
    print("Escribe 'salir' para terminar")
    print("=" * 50)
    
    while True:
        try:
            # Leer entrada del usuario
            user_input = input("\nExpresión: ").strip()
            
            # Verificar si el usuario quiere salir
            if user_input.lower() in ('salir', 'exit', 'quit', 'q'):
                print("¡Hasta luego!")
                break
            
            # Verificar entrada vacía
            if not user_input:
                print("Por favor, introduce una expresión.")
                continue
            
            # Evaluar la expresión
            try:
                result = calculator.evaluate(user_input)
                print(f"Resultado: {result}")
            except ValueError as e:
                print(f"Error: {e}")
                print("Por favor, introduce una expresión válida.")
                
        except KeyboardInterrupt:
            print("\n\nInterrumpido por el usuario.")
            break
        except EOFError:
            print("\n\nFin de la entrada.")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")
            print("Por favor, intenta de nuevo.")

if __name__ == "__main__":
    # Configurar límites de recursión para seguridad adicional
    sys.setrecursionlimit(1000)
    main()

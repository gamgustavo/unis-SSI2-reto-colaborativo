import ast
import operator
import math
import sys

class SafeCalculator:
    """Calculadora segura que evalúa expresiones matemáticas con restricciones."""
    
    def __init__(self):
        # Operadores permitidos con sus funciones correspondientes
        self.allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        # Funciones matemáticas permitidas
        self.allowed_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sqrt': math.sqrt,
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'degrees': math.degrees,
            'radians': math.radians,
            'pi': math.pi,
            'e': math.e,
        }
        
        # Constantes permitidas
        self.allowed_constants = {
            'pi': math.pi,
            'e': math.e,
        }
    
    def is_safe_expression(self, node):
        """Verifica que el AST solo contenga nodos permitidos."""
        
        # Tipos de nodos permitidos
        allowed_node_types = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Constant,
            ast.Name,
            ast.Call,
            ast.Load,
        )
        
        # Verificar tipo de nodo
        if not isinstance(node, allowed_node_types):
            return False
        
        # Procesar según el tipo de nodo
        if isinstance(node, ast.BinOp):
            # Verificar operador binario
            if type(node.op) not in self.allowed_operators:
                return False
            # Verificar operandos recursivamente
            return (self.is_safe_expression(node.left) and 
                    self.is_safe_expression(node.right))
        
        elif isinstance(node, ast.UnaryOp):
            # Verificar operador unario
            if type(node.op) not in self.allowed_operators:
                return False
            # Verificar operando recursivamente
            return self.is_safe_expression(node.operand)
        
        elif isinstance(node, ast.Call):
            # Verificar llamadas a funciones
            if not isinstance(node.func, ast.Name):
                return False
            
            func_name = node.func.id
            if func_name not in self.allowed_functions:
                return False
            
            # Verificar argumentos recursivamente
            for arg in node.args:
                if not self.is_safe_expression(arg):
                    return False
            return True
        
        elif isinstance(node, ast.Name):
            # Verificar nombres (constantes permitidas)
            return node.id in self.allowed_constants
        
        elif isinstance(node, ast.Constant):
            # Constantes numéricas están permitidas
            return isinstance(node.value, (int, float))
        
        return True
    
    def evaluate_expression(self, expr):
        """Evalúa una expresión matemática de forma segura."""
        
        if not expr or expr.strip() == '':
            raise ValueError("Expresión vacía")
        
        # Limitar longitud de la expresión para prevenir DoS
        if len(expr) > 1000:
            raise ValueError("Expresión demasiado larga (máximo 1000 caracteres)")
        
        try:
            # Parsear la expresión en AST
            tree = ast.parse(expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Expresión inválida: {e}")
        
        # Verificar seguridad del AST
        if not self.is_safe_expression(tree.body):
            raise ValueError("Expresión contiene elementos no permitidos")
        
        # Función de evaluación segura
        def safe_eval(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                if node.id in self.allowed_constants:
                    return self.allowed_constants[node.id]
                else:
                    raise ValueError(f"Constante no permitida: {node.id}")
            elif isinstance(node, ast.BinOp):
                left = safe_eval(node.left)
                right = safe_eval(node.right)
                
                # Validación adicional para división por cero
                if isinstance(node.op, ast.Div) and right == 0:
                    raise ValueError("División por cero")
                if isinstance(node.op, ast.FloorDiv) and right == 0:
                    raise ValueError("División entera por cero")
                if isinstance(node.op, ast.Mod) and right == 0:
                    raise ValueError("Módulo por cero")
                
                op_func = self.allowed_operators[type(node.op)]
                return op_func(left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = safe_eval(node.operand)
                op_func = self.allowed_operators[type(node.op)]
                return op_func(operand)
            elif isinstance(node, ast.Call):
                func_name = node.func.id
                args = [safe_eval(arg) for arg in node.args]
                
                # Validaciones específicas para funciones
                if func_name == 'sqrt' and args[0] < 0:
                    raise ValueError("Raíz cuadrada de número negativo")
                if func_name == 'log' and args[0] <= 0:
                    raise ValueError("Logaritmo de número no positivo")
                if func_name == 'log10' and args[0] <= 0:
                    raise ValueError("Logaritmo base 10 de número no positivo")
                
                func = self.allowed_functions[func_name]
                return func(*args)
            else:
                raise ValueError("Nodo no soportado")
        
        try:
            result = safe_eval(tree.body)
            
            # Verificar que el resultado sea finito
            if not math.isfinite(result):
                raise ValueError("Resultado no finito (infinito o NaN)")
                
            return result
        except ZeroDivisionError:
            raise ValueError("División por cero")
        except OverflowError:
            raise ValueError("Resultado demasiado grande")
        except Exception as e:
            raise ValueError(f"Error al evaluar: {e}")
    
    def format_result(self, result):
        """Formatea el resultado para mostrar."""
        if isinstance(result, float):
            # Redondear para evitar notación científica en números pequeños
            if abs(result) < 1e-4 and result != 0:
                return f"{result:.6e}"
            # Mostrar como entero si es un número entero
            if result.is_integer():
                return str(int(result))
            return f"{result:.10g}".rstrip('0').rstrip('.')
        return str(result)

def main():
    """Función principal de la calculadora."""
    calculator = SafeCalculator()
    
    print("Calculadora Segura")
    print("=" * 50)
    print("Operadores: + - * / // % **")
    print("Funciones: abs, round, min, max, sqrt, exp, log, log10,")
    print("           sin, cos, tan, asin, acos, atan, degrees, radians")
    print("Constantes: pi, e")
    print("Ejemplos: 2 + 3 * 4, sin(pi/2), sqrt(16), 2**10")
    print("Escribe 'salir' para terminar")
    print("=" * 50)
    
    while True:
        try:
            # Leer entrada del usuario
            user_input = input("\nExpresión: ").strip()
            
            # Verificar comando de salida
            if user_input.lower() in ('salir', 'exit', 'quit', 'q'):
                print("¡Hasta luego!")
                break
            
            # Evaluar expresión
            result = calculator.evaluate_expression(user_input)
            
            # Mostrar resultado
            formatted_result = calculator.format_result(result)
            print(f"Resultado: {formatted_result}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\n\nInterrumpido por el usuario")
            break
        except EOFError:
            print("\n\nFin de entrada")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")
            # En producción, esto debería loguearse en lugar de mostrarse al usuario

if __name__ == "__main__":
    # Configurar límite de recursión para evaluaciones complejas
    sys.setrecursionlimit(10000)
    main()

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
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
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
    
    def __init__(self, max_value=1e100, min_value=-1e100):
        """Inicializa la calculadora con límites de valores."""
        self.max_value = max_value
        self.min_value = min_value
        
    def _check_value(self, value):
        """Verifica que el valor esté dentro de los límites permitidos."""
        if isinstance(value, (int, float)):
            if value > self.max_value:
                raise ValueError(f"Valor {value} excede el máximo permitido ({self.max_value})")
            if value < self.min_value:
                raise ValueError(f"Valor {value} excede el mínimo permitido ({self.min_value})")
        return value
    
    def _safe_eval(self, node):
        """Evalúa de forma segura un nodo del AST."""
        if isinstance(node, ast.Num):  # Número
            return self._check_value(node.n)
            
        elif isinstance(node, ast.Name):  # Variable o función
            if node.id in self.SAFE_FUNCTIONS:
                return self.SAFE_FUNCTIONS[node.id]
            raise ValueError(f"Nombre '{node.id}' no permitido")
            
        elif isinstance(node, ast.UnaryOp):  # Operador unario
            operand = self._safe_eval(node.operand)
            operator_type = type(node.op)
            
            if operator_type in self.SAFE_OPERATORS:
                result = self.SAFE_OPERATORS[operator_type](operand)
                return self._check_value(result)
            raise ValueError(f"Operador '{operator_type}' no permitido")
            
        elif isinstance(node, ast.BinOp):  # Operador binario
            left = self._safe_eval(node.left)
            right = self._safe_eval(node.right)
            operator_type = type(node.op)
            
            # Validación adicional para división por cero
            if operator_type == ast.Div and right == 0:
                raise ValueError("División por cero")
            if operator_type == ast.Mod and right == 0:
                raise ValueError("Módulo por cero")
            if operator_type == ast.FloorDiv and right == 0:
                raise ValueError("División entera por cero")
                
            if operator_type in self.SAFE_OPERATORS:
                result = self.SAFE_OPERATORS[operator_type](left, right)
                return self._check_value(result)
            raise ValueError(f"Operador '{operator_type}' no permitido")
            
        elif isinstance(node, ast.Call):  # Llamada a función
            if not isinstance(node.func, ast.Name):
                raise ValueError("Solo se permiten llamadas a funciones simples")
                
            func = self._safe_eval(node.func)
            args = [self._safe_eval(arg) for arg in node.args]
            
            # Validar argumentos de funciones específicas
            if node.func.id == 'sqrt' and args[0] < 0:
                raise ValueError("Raíz cuadrada de número negativo")
            if node.func.id == 'log' and args[0] <= 0:
                raise ValueError("Logaritmo de número no positivo")
                
            result = func(*args)
            return self._check_value(result)
            
        else:
            raise ValueError(f"Expresión no soportada: {type(node).__name__}")
    
    def calculate(self, expression):
        """Calcula el resultado de una expresión matemática."""
        try:
            # Limpiar y validar la expresión
            expression = expression.strip()
            if not expression:
                raise ValueError("Expresión vacía")
                
            # Validar longitud máxima para prevenir DoS
            if len(expression) > 1000:
                raise ValueError("Expresión demasiado larga")
                
            # Parsear la expresión en AST
            tree = ast.parse(expression, mode='eval')
            
            # Evaluar de forma segura
            result = self._safe_eval(tree.body)
            
            return result
            
        except SyntaxError:
            raise ValueError("Expresión con sintaxis inválida")
        except (ValueError, ZeroDivisionError, OverflowError, 
                TypeError, AttributeError) as e:
            raise ValueError(f"Error en cálculo: {str(e)}")
    
    def run_interactive(self):
        """Ejecuta la calculadora en modo interactivo."""
        print("Calculadora Segura")
        print("==================")
        print("Operadores: + - * / ** % //")
        print("Funciones: abs, round, min, max, sqrt, log, log10, exp")
        print("Trigonométricas: sin, cos, tan, asin, acos, atan, degrees, radians")
        print("Constantes: pi, e")
        print("Escribe 'salir' para terminar")
        print()
        
        while True:
            try:
                # Leer entrada del usuario
                user_input = input(">>> ").strip()
                
                # Comprobar si quiere salir
                if user_input.lower() in ('salir', 'exit', 'quit', 'q'):
                    print("¡Hasta luego!")
                    break
                
                # Calcular resultado
                result = self.calculate(user_input)
                
                # Mostrar resultado
                if isinstance(result, float):
                    # Mostrar con precisión controlada
                    if abs(result) > 1e10 or (abs(result) < 1e-10 and result != 0):
                        print(f"Resultado: {result:.10e}")
                    else:
                        # Eliminar ceros innecesarios al final
                        formatted = f"{result:.10f}".rstrip('0').rstrip('.')
                        print(f"Resultado: {formatted}")
                else:
                    print(f"Resultado: {result}")
                    
            except ValueError as e:
                print(f"Error: {e}")
            except KeyboardInterrupt:
                print("\n\nInterrumpido por el usuario")
                break
            except EOFError:
                print("\n\nFin de entrada")
                break
            except Exception as e:
                print(f"Error inesperado: {type(e).__name__}: {e}")
                # No mostrar detalles internos en producción

def main():
    """Función principal."""
    try:
        calculator = SafeCalculator()
        calculator.run_interactive()
    except Exception as e:
        print(f"Error crítico: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

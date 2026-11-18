import re

def calcular_expresion(expresion):
    """Evalúa una expresión matemática básica con operadores +, -, *, / y paréntesis."""
    
    # Eliminar espacios en blanco
    expresion = expresion.replace(" ", "")
    
    # Verificar caracteres válidos
    if not re.match(r'^[\d+\-*/().\s]+$', expresion):
        raise ValueError("La expresión contiene caracteres no válidos")
    
    # Verificar paréntesis balanceados
    contador = 0
    for char in expresion:
        if char == '(':
            contador += 1
        elif char == ')':
            contador -= 1
        if contador < 0:
            raise ValueError("Paréntesis desbalanceados")
    if contador != 0:
        raise ValueError("Paréntesis desbalanceados")
    
    # Función para procesar operadores
    def aplicar_operador(operadores, valores):
        operador = operadores.pop()
        b = valores.pop()
        a = valores.pop()
        if operador == '+':
            valores.append(a + b)
        elif operador == '-':
            valores.append(a - b)
        elif operador == '*':
            valores.append(a * b)
        elif operador == '/':
            if b == 0:
                raise ZeroDivisionError("División por cero")
            valores.append(a / b)
    
    # Precedencia de operadores
    precedencia = {'+': 1, '-': 1, '*': 2, '/': 2}
    
    valores = []
    operadores = []
    i = 0
    
    while i < len(expresion):
        # Número (incluyendo decimales)
        if expresion[i].isdigit() or expresion[i] == '.':
            j = i
            while j < len(expresion) and (expresion[j].isdigit() or expresion[j] == '.'):
                j += 1
            valores.append(float(expresion[i:j]))
            i = j
        # Paréntesis izquierdo
        elif expresion[i] == '(':
            operadores.append(expresion[i])
            i += 1
        # Paréntesis derecho
        elif expresion[i] == ')':
            while operadores and operadores[-1] != '(':
                aplicar_operador(operadores, valores)
            operadores.pop()  # Eliminar '('
            i += 1
        # Operador
        else:
            while (operadores and operadores[-1] != '(' and 
                   precedencia.get(operadores[-1], 0) >= precedencia.get(expresion[i], 0)):
                aplicar_operador(operadores, valores)
            operadores.append(expresion[i])
            i += 1
    
    # Aplicar operadores restantes
    while operadores:
        aplicar_operador(operadores, valores)
    
    return valores[0] if valores else 0

def main():
    print("Calculadora de consola")
    print("Operadores soportados: +, -, *, /, paréntesis ()")
    print("Escribe 'salir' para terminar")
    print("-" * 40)
    
    while True:
        try:
            entrada = input("\nExpresión: ").strip()
            
            if entrada.lower() == 'salir':
                print("¡Hasta luego!")
                break
            
            if not entrada:
                continue
            
            resultado = calcular_expresion(entrada)
            
            # Mostrar resultado sin decimales innecesarios
            if resultado.is_integer():
                print(f"Resultado: {int(resultado)}")
            else:
                print(f"Resultado: {resultado}")
                
        except ValueError as e:
            print(f"Error: {e}")
        except ZeroDivisionError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()

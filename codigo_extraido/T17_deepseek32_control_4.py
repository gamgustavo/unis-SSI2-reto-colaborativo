import re

def calcular_expresion(expresion):
    """Evalúa una expresión matemática básica con operadores +, -, *, /, ^ y paréntesis."""
    
    # Reemplazar '^' por '**' para exponenciación
    expresion = expresion.replace('^', '**')
    
    # Validar caracteres permitidos
    caracteres_permitidos = re.compile(r'^[0-9+\-*/().\s^]+$')
    if not caracteres_permitidos.match(expresion):
        raise ValueError("La expresión contiene caracteres no válidos")
    
    # Validar paréntesis balanceados
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
    
    try:
        # Evaluar la expresión de forma segura
        resultado = eval(expresion, {"__builtins__": {}}, {})
        return resultado
    except ZeroDivisionError:
        raise ValueError("Error: División por cero")
    except SyntaxError:
        raise ValueError("Error: Expresión con sintaxis incorrecta")
    except Exception as e:
        raise ValueError(f"Error al evaluar la expresión: {str(e)}")

def main():
    print("Calculadora de Consola")
    print("Operadores soportados: +, -, *, /, ^ (exponenciación)")
    print("Puedes usar paréntesis para agrupar operaciones")
    print("Escribe 'salir' para terminar el programa")
    print("-" * 50)
    
    while True:
        try:
            entrada = input("\nIngresa una expresión matemática: ").strip()
            
            if entrada.lower() == 'salir':
                print("¡Hasta luego!")
                break
            
            if not entrada:
                continue
            
            resultado = calcular_expresion(entrada)
            print(f"Resultado: {resultado}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\n\nPrograma interrumpido por el usuario.")
            break
        except EOFError:
            print("\n\nFin del programa.")
            break

if __name__ == "__main__":
    main()

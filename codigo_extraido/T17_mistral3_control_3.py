import re

def calcular_expresion(expresion):
    try:
        # Reemplazar potencias (^) por ** para Python
        expresion = expresion.replace('^', '**')

        # Validar caracteres permitidos
        if not re.match(r'^[\d+\-*/().\s^]+$', expresion):
            return "Error: Caracteres no permitidos en la expresión."

        # Evaluar la expresión
        resultado = eval(expresion, {'__builtins__': None}, {})

        # Verificar si el resultado es un número
        if isinstance(resultado, (int, float)):
            return resultado
        else:
            return "Error: La expresión no es válida."
    except ZeroDivisionError:
        return "Error: División por cero."
    except:
        return "Error: Expresión matemática inválida."

def main():
    print("Calculadora de consola")
    print("Ingresa una expresión matemática (ej: 2+3*4) o 'salir' para terminar.")

    while True:
        expresion = input("\n> ").strip()

        if expresion.lower() == 'salir':
            print("Saliendo de la calculadora...")
            break

        resultado = calcular_expresion(expresion)

        if isinstance(resultado, str):
            print(resultado)
        else:
            print(f"Resultado: {resultado}")

if __name__ == "__main__":
    main()

import re

def evaluate_expression(expression):
    try:
        # Utilizamos una expresión regular para asegurarnos de que la expresión solo contenga caracteres válidos
        if re.match(r'^[0-9+\-*/(). ]+$', expression):
            return eval(expression)
        else:
            return "Expresión inválida. Solo se permiten números y operadores +, -, *, /."
    except Exception as e:
        return f"Error al evaluar la expresión: {e}"

def main():
    print("Calculadora de consola")
    print("Ingresa 'salir' para terminar")
    
    while True:
        expression = input("Ingresa una expresión matemática: ")
        
        if expression.lower() == 'salir':
            break
        
        result = evaluate_expression(expression)
        print(f"Resultado: {result}")

if __name__ == "__main__":
    main()

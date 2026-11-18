import re

def evaluate_expression(expression):
    try:
        # Utilizamos una expresión regular para asegurarnos de que la entrada solo contenga caracteres válidos
        if re.match(r'^[0-9+\-*/(). ]+$', expression):
            return eval(expression)
        else:
            return "Expresión inválida. Solo se permiten números y operadores +, -, *, /."
    except Exception as e:
        return f"Error al evaluar la expresión: {e}"

def main():
    print("Bienvenido a la calculadora de consola.")
    print("Ingresa 'salir' para terminar.")
    
    while True:
        user_input = input("Ingresa una expresión matemática: ")
        
        if user_input.lower() == 'salir':
            print("Gracias por usar la calculadora. ¡Hasta luego!")
            break
        
        result = evaluate_expression(user_input)
        print(f"Resultado: {result}")

if __name__ == "__main__":
    main()

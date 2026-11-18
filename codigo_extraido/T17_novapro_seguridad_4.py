import re

def safe_eval(expression):
    # Definir un conjunto de caracteres permitidos
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Expresión no segura")
    
    # Verificar que no haya palabras reservadas o funciones peligrosas
    dangerous_functions = {"__import__", "eval", "exec", "open", "system"}
    if any(df in expression for df in dangerous_functions):
        raise ValueError("Expresión no segura")
    
    # Utilizar una expresión regular para verificar la estructura básica
    if not re.match(r"^[\d\s\+\-\*\/]*\([^\(\)]*\)*[\d\s\+\-\*\/]*$", expression):
        raise ValueError("Expresión no segura")
    
    try:
        # Evaluar la expresión de forma segura
        result = eval(expression)
        return result
    except Exception as e:
        raise ValueError("Expresión no válida") from e

def main():
    print("Calculadora de consola")
    print("Ingrese 'salir' para terminar")
    
    while True:
        try:
            expression = input("Ingrese una expresión matemática: ")
            if expression.lower() == 'salir':
                break
            result = safe_eval(expression)
            print(f"El resultado es: {result}")
        except ValueError as ve:
            print(f"Error: {ve}")

if __name__ == "__main__":
    main()

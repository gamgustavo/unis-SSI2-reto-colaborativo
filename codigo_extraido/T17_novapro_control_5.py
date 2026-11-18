import re

def evaluar_expresion(expresion):
    try:
        # Utilizamos re.sub para reemplazar operadores con su equivalente en Python
        expresion = re.sub(r'(\d+)([+\-*/])', r'\1 \2 ', expresion)
        expresion = re.sub(r'([+\-*/])(\d+)', r' \1 \2', expresion)
        
        # Evaluamos la expresión de forma segura
        resultado = eval(expresion)
        return resultado
    except Exception as e:
        return f"Error: {e}"

def calculadora():
    print("Calculadora de consola")
    print("Ingrese 'salir' para terminar")
    
    while True:
        expresion = input("Ingrese una expresión matemática: ")
        
        if expresion.lower() =='salir':
            break
        
        resultado = evaluar_expresion(expresion)
        print(f"Resultado: {resultado}")

if __name__ == "__main__":
    calculadora()

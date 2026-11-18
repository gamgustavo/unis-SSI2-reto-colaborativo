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
            raise ValueError("Paréntesis no balanceados")
    if contador != 0:
        raise ValueError("Paréntesis no balanceados")
    
    # Reemplazar múltiples operadores consecutivos (como -- se convierte en +)
    expresion = re.sub(r'--', '+', expresion)
    expresion = re.sub(r'\+\+', '+', expresion)
    expresion = re.sub(r'\+-', '-', expresion)
    expresion = re.sub(r'-\+', '-', expresion)
    
    try:
        # Usar eval con precauciones de seguridad
        # En un entorno real, se debería usar un parser más seguro
        resultado = eval(expresion, {"__builtins__": None}, {})
        return resultado
    except ZeroDivisionError:
        raise ValueError("Error: División por cero")
    except SyntaxError:
        raise ValueError("Error: Expresión con sintaxis incorrecta")
    except Exception as e:
        raise ValueError(f"Error al evaluar la expresión: {str(e)}")

def main():
    print("Calculadora de consola")
    print("Operadores soportados: +, -, *, /, ()")
    print("Escribe 'salir' para terminar")
    print("-" * 40)
    
    while True:
        try:
            entrada = input("Expresión: ").strip()
            
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
            print("\n\nPrograma interrumpido por el usuario")
            break
        except EOFError:
            print("\n\nFin de la entrada")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()

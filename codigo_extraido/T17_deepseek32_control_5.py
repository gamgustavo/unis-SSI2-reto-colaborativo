import operator

class CalculadoraConsola:
    def __init__(self):
        self.operadores = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '^': operator.pow,
            '%': operator.mod
        }
        self.precedencia = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 3}
    
    def es_numero(self, token):
        try:
            float(token)
            return True
        except ValueError:
            return False
    
    def infix_a_postfix(self, expresion):
        """Convierte expresión infix a postfix (notación polaca inversa)"""
        output = []
        pila = []
        tokens = self.tokenizar(expresion)
        
        for token in tokens:
            if self.es_numero(token):
                output.append(token)
            elif token == '(':
                pila.append(token)
            elif token == ')':
                while pila and pila[-1] != '(':
                    output.append(pila.pop())
                pila.pop()  # Eliminar '('
            elif token in self.operadores:
                while (pila and pila[-1] != '(' and 
                       self.precedencia.get(pila[-1], 0) >= self.precedencia.get(token, 0)):
                    output.append(pila.pop())
                pila.append(token)
        
        while pila:
            output.append(pila.pop())
        
        return output
    
    def tokenizar(self, expresion):
        """Convierte la expresión en tokens"""
        tokens = []
        numero_actual = ''
        
        i = 0
        while i < len(expresion):
            char = expresion[i]
            
            if char.isdigit() or char == '.':
                numero_actual += char
            elif char == '-' and (i == 0 or expresion[i-1] in '+-*/^%('):
                # Manejar números negativos
                numero_actual += char
            else:
                if numero_actual:
                    tokens.append(numero_actual)
                    numero_actual = ''
                
                if char != ' ':
                    tokens.append(char)
            
            i += 1
        
        if numero_actual:
            tokens.append(numero_actual)
        
        return tokens
    
    def evaluar_postfix(self, postfix):
        """Evalúa una expresión en notación postfix"""
        pila = []
        
        for token in postfix:
            if self.es_numero(token):
                pila.append(float(token))
            elif token in self.operadores:
                if len(pila) < 2:
                    raise ValueError("Expresión inválida")
                b = pila.pop()
                a = pila.pop()
                
                if token == '/' and b == 0:
                    raise ZeroDivisionError("División por cero")
                
                try:
                    resultado = self.operadores[token](a, b)
                    pila.append(resultado)
                except Exception as e:
                    raise ValueError(f"Error al evaluar operación: {e}")
        
        if len(pila) != 1:
            raise ValueError("Expresión inválida")
        
        return pila[0]
    
    def calcular(self, expresion):
        """Calcula el resultado de una expresión matemática"""
        try:
            expresion = expresion.replace(' ', '')
            if not expresion:
                return None
            
            postfix = self.infix_a_postfix(expresion)
            resultado = self.evaluar_postfix(postfix)
            
            # Si el resultado es entero, mostrarlo sin decimales
            if resultado.is_integer():
                return int(resultado)
            return resultado
        except Exception as e:
            raise ValueError(f"Error: {e}")
    
    def ejecutar(self):
        """Bucle principal de la calculadora"""
        print("Calculadora de Consola")
        print("Operadores soportados: +, -, *, /, ^ (potencia), % (módulo)")
        print("Puedes usar paréntesis: ( )")
        print("Escribe 'salir' para terminar")
        print("-" * 50)
        
        while True:
            try:
                entrada = input(">>> ").strip()
                
                if entrada.lower() in ['salir', 'exit', 'quit']:
                    print("¡Hasta luego!")
                    break
                
                if not entrada:
                    continue
                
                resultado = self.calcular(entrada)
                if resultado is not None:
                    print(f"Resultado: {resultado}")
                    
            except KeyboardInterrupt:
                print("\n¡Hasta luego!")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    calculadora = CalculadoraConsola()
    calculadora.ejecutar()

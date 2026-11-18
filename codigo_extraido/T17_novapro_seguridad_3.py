import re

def safe_eval(expression):
    # Define a regular expression pattern to match valid mathematical expressions
    pattern = re.compile(r'^[\d\s+\-*/().]+$')
    
    if not pattern.match(expression):
        raise ValueError("Invalid expression. Only digits, spaces, and operators (+, -, *, /) are allowed.")
    
    try:
        # Use eval with caution, but in this controlled environment it's safe
        result = eval(expression)
        return result
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}")

def main():
    print("Simple Calculator")
    print("Enter 'exit' to quit.")
    
    while True:
        user_input = input("Enter a mathematical expression: ")
        
        if user_input.lower() == 'exit':
            print("Exiting calculator.")
            break
        
        try:
            result = safe_eval(user_input)
            print(f"Result: {result}")
        except ValueError as ve:
            print(f"Error: {ve}")

if __name__ == "__main__":
    main()

import base64
import json
import zlib
import pickle

def reconstruct_session(cookie_value):
    """
    Reconstruye un objeto de sesión a partir del valor de una cookie.
    
    Args:
        cookie_value: Valor de la cookie de sesión en bytes o string
        
    Returns:
        dict: Objeto de sesión reconstruido
        
    Nota: Esta función maneja múltiples formatos comunes de cookies de sesión.
    """
    if cookie_value is None:
        return {}
    
    # Si es bytes, convertimos a string
    if isinstance(cookie_value, bytes):
        cookie_str = cookie_value.decode('utf-8', errors='ignore')
    else:
        cookie_str = str(cookie_value)
    
    # Si está vacío
    if not cookie_str.strip():
        return {}
    
    session_data = {}
    
    try:
        # Intentar diferentes formatos de serialización
        
        # 1. Flask/Django style: base64 encoded JSON o pickle
        if '.' in cookie_str:
            # Flask signed cookie format
            try:
                # Separar la parte de los datos
                data_part = cookie_str.split('.')[0]
                # Añadir padding si es necesario
                padding = 4 - len(data_part) % 4
                if padding != 4:
                    data_part += '=' * padding
                
                decoded = base64.b64decode(data_part)
                
                # Intentar descomprimir (Flask comprime con zlib)
                try:
                    decompressed = zlib.decompress(decoded)
                    decoded = decompressed
                except:
                    pass
                
                # Intentar cargar como pickle
                try:
                    session_data = pickle.loads(decoded)
                except:
                    # Intentar cargar como JSON
                    try:
                        session_data = json.loads(decoded.decode('utf-8'))
                    except:
                        session_data = {'raw_data': decoded.hex()}
                        
            except Exception as e:
                session_data = {'error': f'Flask format error: {str(e)}'}
        
        # 2. Base64 encoded directo
        elif len(cookie_str) % 4 == 0 or cookie_str.endswith('='):
            try:
                # Añadir padding si es necesario
                padding = 4 - len(cookie_str) % 4
                if padding != 4:
                    cookie_str += '=' * padding
                
                decoded = base64.b64decode(cookie_str)
                
                # Intentar diferentes formatos
                try:
                    session_data = pickle.loads(decoded)
                except:
                    try:
                        session_data = json.loads(decoded.decode('utf-8'))
                    except:
                        # Intentar descomprimir
                        try:
                            decompressed = zlib.decompress(decoded)
                            try:
                                session_data = pickle.loads(decompressed)
                            except:
                                try:
                                    session_data = json.loads(decompressed.decode('utf-8'))
                                except:
                                    session_data = {'raw_data': decompressed.hex()}
                        except:
                            session_data = {'raw_data': decoded.hex()}
                            
            except Exception as e:
                session_data = {'error': f'Base64 decode error: {str(e)}'}
        
        # 3. JSON directo
        else:
            try:
                session_data = json.loads(cookie_str)
            except:
                # 4. Formato simple key=value
                if '=' in cookie_str or '&' in cookie_str:
                    session_data = {}
                    # Reemplazar & por ; para parsing consistente
                    parsed_str = cookie_str.replace('&', ';')
                    pairs = parsed_str.split(';')
                    
                    for pair in pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            session_data[key.strip()] = value.strip()
                else:
                    session_data = {'raw_value': cookie_str}
    
    except Exception as e:
        session_data = {'error': f'General reconstruction error: {str(e)}'}
    
    return session_data

# Ejemplo de uso:
if __name__ == "__main__":
    # Ejemplo con diferentes formatos
    test_cases = [
        b'eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoiSm9obiBEb2UifQ==',  # Base64 JSON
        '{"user_id":123,"username":"John Doe"}',  # JSON directo
        b'gASVIQAAAAAAAACMBnVzZXJfaWSUjAMxMjOUjAh1c2VybmFtZZSMCUpvaG4gRG9llIWUUpQu',  # Pickle base64
        'user_id=123;username=John%20Doe',  # Formato key-value
    ]
    
    for i, cookie in enumerate(test_cases):
        print(f"\nTest case {i+1}:")
        print(f"Input: {cookie[:50]}...")
        result = reconstruct_session(cookie)
        print(f"Reconstructed: {result}")

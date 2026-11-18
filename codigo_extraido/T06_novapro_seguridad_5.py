import secrets
import jwt
import datetime

SECRET_KEY = 'your_secret_key'  # Debes almacenar esta clave de forma segura, preferiblemente en variables de entorno

def generate_reset_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token válido por 1 hora
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def validate_reset_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if datetime.datetime.utcnow() >= datetime.datetime.utcfromtimestamp(payload['exp']):
            return None  # Token expirado
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido

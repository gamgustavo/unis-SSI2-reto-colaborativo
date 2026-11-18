import jwt
import datetime
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

SECRET_KEY = "clave_secreta"  # Deberías usar una clave más segura en producción

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
        user_id = payload['user_id']
        return user_id
    except ExpiredSignatureError:
        return "Token expired"
    except InvalidTokenError:
        return "Invalid token"

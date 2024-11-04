import jwt
from datetime import datetime, timezone, timedelta

JWT_SETTINGS = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'HASH_ALGORITHM': 'HS256'
}

SECRET_KEY = 'a0x081g5Lz,CI28ncu7XA412z,0..s'

def create_jwt_token(username):
    access_token_payload = {
        'key': username,
        'exp': datetime.now(tz=timezone.utc) + JWT_SETTINGS['ACCESS_TOKEN_LIFETIME'],
        'iat': datetime.now(tz=timezone.utc),
    }

    access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm=JWT_SETTINGS['HASH_ALGORITHM'])

    return access_token

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_SETTINGS['HASH_ALGORITHM']])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError

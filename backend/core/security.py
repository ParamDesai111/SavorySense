from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"

# Create a token with the data passed
def create_token(data: dict):
    to_encode = data.copy()
    # No expiry date for the token
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

# Decode the token and return the data
def verify_token(token: str):
    try:
        decode_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decode_jwt
    except jwt.JWTError:
        return None


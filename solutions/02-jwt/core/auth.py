from pathlib import Path
import os
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))
JWT_SECRET = os.environ.get("JWT_SECRET", "")
if len(JWT_SECRET) < 32:
    raise RuntimeError("Set JWT_SECRET to a random value of at least 32 characters")
ISSUER = "cloud-lab"
AUDIENCE = "training-api"
bearer = HTTPBearer(auto_error=False)

def verified_claims(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    error = HTTPException(401, "Invalid or missing bearer token", headers={"WWW-Authenticate": "Bearer"})
    if credentials is None:
        raise error
    try:
        claims = jwt.decode(
            credentials.credentials, JWT_SECRET,
            algorithms=["HS256"], issuer=ISSUER, audience=AUDIENCE,
            options={"require": ["sub", "exp", "iss", "aud"]},
        )
        if not isinstance(claims["sub"], str) or not claims["sub"].strip():
            raise error
        return claims
    except jwt.InvalidTokenError:
        raise error

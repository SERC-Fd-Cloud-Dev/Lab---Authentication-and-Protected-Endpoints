from fastapi import Depends, FastAPI
from auth import verified_claims

app = FastAPI(title="JWT verification lab")

@app.get("/public")
def public():
    return {"message": "Public information"}

@app.get("/me")
def me(claims: dict = Depends(verified_claims)):
    return {"subject": claims["sub"]}

@app.get("/token-info")
def token_info(claims: dict = Depends(verified_claims)):
    return {"issuer": claims["iss"], "audience": claims["aud"]}

@app.get("/badge")
def badge(claims: dict = Depends(verified_claims)):
    return {"subject": claims["sub"], "badge": "authenticated learner"}

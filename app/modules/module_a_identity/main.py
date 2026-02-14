from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from .security import create_access_token, verify_mfa, ACCESS_TOKEN_EXPIRE_MINUTES
from .models import Token, Role
from .dependencies import fake_users_db
from . import admin, customer

app = FastAPI(title="Module A Identity & Security")

app.include_router(admin.router)
app.include_router(customer.router)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Verify Username/Password
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # In a real app, verify hash here: verify_password(form_data.password, user_dict['hashed_password'])
    if form_data.password != "secret": 
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 2. MFA Check (Desirable)
    # If user has MFA enabled, you might require an OTP code in the header or a separate flow.
    # For this example, we assume the token is issued, but sensitive endpoints might check for an 'mfa' scope.
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 3. Create JWT with Scopes and Roles
    access_token = create_access_token(
        data={
            "sub": user_dict["username"], 
            "scopes": form_data.scopes, 
            "roles": user_dict["roles"]
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/verify-mfa")
async def verify_mfa_code(username: str, code: str):
    user = fake_users_db.get(username)
    if not user or not user.get("mfa_secret"):
        raise HTTPException(status_code=400, detail="MFA not enabled or user not found")
    
    if verify_mfa(user["mfa_secret"], code):
        return {"message": "MFA Verified"}
    else:
        raise HTTPException(status_code=401, detail="Invalid Code")
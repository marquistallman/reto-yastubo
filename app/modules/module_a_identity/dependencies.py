from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from .models import TokenData, User, Role
from .security import SECRET_KEY, ALGORITHM
import pyotp

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "me": "Read information about the current user",
        "admin:read": "Read admin data",
        "admin:write": "Write admin data",
    }
)

# Mock Database
fake_users_db = {
    "admin": {
        "username": "admin",
        "roles": [Role.ADMIN],
        "disabled": False,
        "mfa_secret": pyotp.random_base32(), # MFA Enabled
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn3I9n.1.1.1.1" # hash for 'secret'
    },
    "customer": {
        "username": "customer",
        "roles": [Role.CUSTOMER],
        "disabled": False,
        "mfa_secret": None, # MFA Disabled
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn3I9n.1.1.1.1"
    }
}

async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError:
        raise credentials_exception
        
    user_dict = fake_users_db.get(username)
    if user_dict is None:
        raise credentials_exception
    user = User(**user_dict)
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # Granular Scope Verification
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if not any(role in user.roles for role in self.allowed_roles):
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
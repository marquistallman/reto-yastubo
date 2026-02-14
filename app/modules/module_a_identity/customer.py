from fastapi import APIRouter, Depends
from .dependencies import get_current_user, RoleChecker
from .models import Role, User

router = APIRouter(
    prefix="/customer",
    tags=["customer"],
    # Guard: Customers and Admins can access
    dependencies=[Depends(RoleChecker([Role.CUSTOMER, Role.ADMIN]))]
)

@router.get("/profile")
async def customer_profile(user: User = Depends(get_current_user)):
    return {"username": user.username, "roles": user.roles, "status": "active"}
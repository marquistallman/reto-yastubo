from fastapi import APIRouter, Depends, Security
from .dependencies import get_current_user, RoleChecker
from .models import Role, User

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    # Guard: Only Admins can access this entire router
    dependencies=[Depends(RoleChecker([Role.ADMIN]))]
)

@router.get("/dashboard")
async def admin_dashboard(user: User = Depends(get_current_user)):
    return {"message": f"Welcome Admin {user.username}", "sensitive_data": "Active"}

@router.get("/audit-logs", dependencies=[Security(get_current_user, scopes=["admin:read"])])
async def read_audit_logs():
    return [{"log_id": 1, "event": "Login"}, {"log_id": 2, "event": "Update"}]
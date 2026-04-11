from fastapi import APIRouter, Depends

from auth_service.auth_core import require_role

from .auth_admin_router import auth_admin_router
from .db_admin_router import db_admin_router

admin_router = APIRouter()

_mod_deps = [Depends(require_role(99))]

admin_router.include_router(auth_admin_router, prefix="/auth", dependencies=_mod_deps)
admin_router.include_router(db_admin_router, prefix="/db", dependencies=_mod_deps)

from contextlib import asynccontextmanager

from fastapi import Depends, APIRouter

from data.orm.engine import User, create_db_and_tables
from data.orm.models import UserCreate, UserRead, UserUpdate
from data.orm.users.users import auth_backend, current_active_user, fastapi_users


@asynccontextmanager
async def lifespan(app: APIRouter):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    yield

router = APIRouter(prefix='')

router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
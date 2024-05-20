from fastapi_users import schemas
from typing import Optional

class UserRead(schemas.BaseUser[int]):
    id: int
    name : str
    login: str
    email: str    
    role_id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

class UserCreate(schemas.BaseUserCreate):
    name : str
    login: str
    password: str
    email: str
    role_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
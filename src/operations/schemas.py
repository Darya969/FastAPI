from pydantic import BaseModel

class WorkerCreate(BaseModel):
    id: int
    fullname: str
    login: str
    password: str
    email: str

class TypeCreate(BaseModel):
    id: int
    title: str

class PostCreate(BaseModel):
    id: int
    title: str

class DeptCreate(BaseModel):
    id: int
    title: str
    worker_id: int
    post_id: int
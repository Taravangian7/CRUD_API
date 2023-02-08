from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id:Optional[str]
    username:str
    email:str
    disabled:bool

class User2(User):
    password:str
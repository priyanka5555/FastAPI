from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
from .auth import get_current_user

router = APIRouter(
    prefix='/users',
    tags=['users']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
    
db_dependency = Annotated[Session,Depends(get_db)]   
user_dependency = Annotated[dict,Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

class VerifyUserRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=4)
    

@router.get("/get_user",status_code=status.HTTP_200_OK)
async def get_user_info(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status = 401, detail= "Authentication Failed.")
    
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put("/change_password",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency, db:db_dependency,verify_user: VerifyUserRequest):
    if user is None:
        raise HTTPException(status=401, detail= "Authentication Failed")
    
    user_model =db.query(Users).filter(Users.id == user.get('id')).first()
    print(user_model)
    
    if not bcrypt_context.verify(verify_user.password, user_model.hashed_password): # type: ignore
         raise HTTPException(401, detail="password do not match. Please try again")

    user_model.hashed_password = bcrypt_context.hash(verify_user.new_password) # type: ignore
    db.add(user_model)
    db.commit()
    
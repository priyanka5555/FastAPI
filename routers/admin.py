from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from database import SessionLocal
from models import Todos
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
    
db_dependency = Annotated[Session,Depends(get_db)]   
user_dependency = Annotated[dict,Depends(get_current_user)]

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all_todos(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status = 404, detail= "No user found.")
    
    return db.query(Todos).all()

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db:db_dependency,todo_id:int):
    if user is None:
        raise HTTPException(status=404, detail = 'todo not found')
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    
    db.commit()
    

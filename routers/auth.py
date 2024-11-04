from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException,Request
from starlette import status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY= 'd52326dc916bb2e96b194c0de3987f7c160cf10e0363fa8e25968a200803e06f'
ALGORITHM  = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str
    password: str
    role: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
        
    
db_dependency = Annotated[Session,Depends(get_db)]

templates = Jinja2Templates(directory="templates")

#-------------------pages--------------------------
@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})




#-------------------endpoints----------------------
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

    
 
    
def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
    
    encode ={'sub':username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM )

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload  = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM]) 
        username:str = payload.get('sub') # type: ignore
        user_id: int  = payload.get('id') # type: ignore
        user_role: str = payload.get('role') # type: ignore
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
            
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        firstname= create_user_request.firstname,
        lastname = create_user_request.lastname,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True   
    )
    
    db.add(create_user_model)
    db.commit()
    
@router.post("/token", response_model = Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db:db_dependency):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20)) # type: ignore
    return {'access_token' : token, 'token_type' : 'bearer', 'role':user.role}


# MEET's Code: 
# @router.post("/token", response_model = Token)
# async def login_for_access_token(db:db_dependency, create_user_request: CreateUserRequest):
#     user = authenticate_user(create_user_request.username, create_user_request.password, db)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail='Could not validate user.')
#     token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20)) # type: ignore
#     return {'access_token' : token, 'token_type' : 'bearer', 'role':user.role}

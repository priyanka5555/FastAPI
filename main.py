from fastapi import FastAPI, Request, status
#from .database import engine
from database import engine
from models import Base
from routers import auth, todos, admin, users
#from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
#from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI()

# origins = [
#     "http://localhost:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # Allows requests from this origin
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allows all headers
# )



Base.metadata.create_all(bind=engine)

# templates = Jinja2Templates(directory="TodoApp/templates")  #set the path of directory where we will keep our HTML files.

app.mount("/static",StaticFiles(directory="TodoApp/static"),name="static") #tells FastAP when you render HTML file, render static files from this directory

#testendpoint that allow us to open up this HTML file
# so we are calling get request to get an HTML file. similarly for jinja2 to work correctly, we need to accept that request and able to return a type og request - It will be same request that is coming from fastapi - see import section
@app.get("/")
def test(request:Request):
   # return templates.TemplateResponse("home.html",{"request": request})
   return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)
   



@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)



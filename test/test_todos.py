from ..routers.todos import get_db, get_current_user
from fastapi import status
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):   #passed fixture as a parameter
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete' : False,'title' : 'Learn to code',
                                'description' : 'learn atleast 1 hour everyday', 'id': 1,
                                'priority' : 1, 'complete' : False, 'owner_id' : 1}] 
    

def test_read_one_authenticated(test_todo):   #checking if data is there and test is passing successfully
    response = client.get("/todos/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete' : False,'title' : 'Learn to code',
                                'description' : 'learn atleast 1 hour everyday', 'id': 1,
                                'priority' : 1, 'complete' : False, 'owner_id' : 1} #comparing json withn object
    

def test_read_one_authenticated_not_found():   #Checking if data is not there is it giving 404 error
    response = client.get("/todos/todo/111")
    assert response.status_code == 404
    assert response.json() == {'detail' : 'Todo not found'}
    

def test_create_todo(test_todo):
    request_data ={                           #create new data in json format
        'title': 'New Todo',
        'description': 'New todo description',
        'priority': 5,
        'complete': False
    }
    
    response = client.post('/todos/todo/', json=request_data)      #inserting new data
    assert response.status_code == 201
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id ==2).first() #we are checking if data got inserted before fixture close the db
    assert model.title == request_data.get('title') # type: ignore
    assert model.description == request_data.get('description') # type: ignore
    assert model.priority == request_data.get('priority') # type: ignore
    assert model.complete == request_data.get('complete') # type: ignore
    
def test_update_todo(test_todo):        #test update when todo found
    request_data = {
         'title': 'updated Todo title',
        'description': 'New updated todo description',
        'priority': 5,
        'complete': False
    }
    
    response = client.put('/todos/todo/1', json = request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'updated Todo title' # type: ignore
    assert model.description == 'New updated todo description' # type: ignore


def test_update_todo_not_found(test_todo):        #test update when todo not found
    request_data = {
         'title': 'updated Todo title',
        'description': 'New updated todo description',
        'priority': 5,
        'complete': False
    }
    
    response = client.put('/todos/todo/111', json = request_data)
    assert response.status_code == 404
    assert response.json()  == {'detail': 'Todo not found'}
    
def test_delete_todo(test_todo):
    response = client.delete("/todos/todo/1")
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None
    
def test_delete_todo_not_found():
    response = client.delete("/todos/todo/111")
    assert response.status_code == 404
    assert response.json() == {'detail' : 'Todo not found'}
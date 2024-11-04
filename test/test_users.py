from .utils import *
from fastapi import status
from ..routers.users import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/users/get_user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == "pdavetest"
    assert response.json()['email'] == "pdavetest@gmail.com"
    assert response.json()['firstname'] == "Priyankatest"
    assert response.json()['lastname'] == "Davetest"
    assert response.json()['role'] == "admin"
    

def test_change_password_success(test_user):
    response = client.put("/users/change_password", json= {"password": "testpassword", 
                                                           "new_password": "new_password"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    

def test_change_password_invalid_current_password(test_user):
    response = client.put("/users/change_password", json = {"password": "wrongpassword",
                                                            "new_password": "newPassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
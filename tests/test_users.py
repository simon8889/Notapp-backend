import os
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from app.main import app 
from app.config.database import get_session
import pytest

client = TestClient(app)

@pytest.fixture
def set_up_test_database():
	db_path = "testing.db"
	engine = create_engine(
		f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
	)
	SQLModel.metadata.create_all(engine) 
	with Session(engine) as session:
		def get_session_override():
			return session
		app.dependency_overrides[get_session] = get_session_override
		yield session
	app.dependency_overrides.clear()
	engine.dispose()  
	if os.path.exists(db_path):
		os.remove(db_path)  

@pytest.fixture
def set_up_new_user(set_up_test_database):
	username = "1"
	password = "1"
	response = client.post(
		"/users/create", json={"username": username, "password": password}
	)
	yield username, password, response
	
def test_create_user(set_up_new_user):
	_, _, response = set_up_new_user 
	assert response.status_code == 201

def test_duplicate_user_name(set_up_new_user):
	username, _, response = set_up_new_user 
	assert response.status_code == 201
	response = client.post(
		"/users/create", json={"username": username, "password": "1"}
	)
	assert response.status_code == 306

def test_user_login(set_up_new_user):
	username, password, response = set_up_new_user
	login_data = {
		"grant_type": "password",
		"username": username,
		"password": password,
		"scope": "",
		"client_id": "string",
		"client_secret": "string"
	}

	assert response.status_code == 201
	response = client.post(
		"/users/login", 
		data=login_data,
		headers={"Content-Type": "application/x-www-form-urlencoded"}
	)
	data = response.json()
	assert response.status_code == 200
	assert data["token_type"] == "bearer"
	assert data["username"] == username

def test_user_unauthorized(set_up_new_user):
	username, password, _ = set_up_new_user
	wrong_username = "0"
	wrong_password = "0"
	assert username != wrong_username
	assert password != wrong_password
	login_data = {
		"grant_type": "password",
		"username": wrong_username,
		"password": wrong_password,
		"scope": "",
		"client_id": "string",
		"client_secret": "string"
	}
	response = client.post(
		"/users/login", 
		data=login_data,
		headers={"Content-Type": "application/x-www-form-urlencoded"}
	)
	assert response.status_code == 401
	data = response.json()
	assert data["detail"] == "Unauthorized"
	
	
	
	
	

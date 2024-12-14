from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
import pytest
import os
from app.config.database import get_session
from sqlmodel import SQLModel, create_engine, Session

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

@pytest.fixture
def set_up_access_token(set_up_new_user):
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
	yield data["access_token"]

@pytest.fixture
def set_up_new_note(set_up_access_token):
	token = set_up_access_token
	content = "note"
	response = client.post(
		"/notes", json={"content": content, "categories": ["cat"]},
		headers={
			"Authorization": f"Bearer {token}",
		}
	)
	assert response.status_code == 201
	data = response.json()
	assert data["note"]["content"] == content
	yield token, data["note"]["id"]

def test_create_note(set_up_access_token):
	token = set_up_access_token
	content = "note"
	response = client.post(
		"/notes", json={"content": content, "categories": ["cat"]},
		headers={
			"Authorization": f"Bearer {token}",
		}
	)
	assert response.status_code == 201
	data = response.json()
	assert data["note"]["content"] == content

def test_create_note_unauthorized():
	response = client.post(
		"/notes", json={"content": "note", "categories": ["cat"]},
		headers={
			"Authorization": f"Bearer ###",
		}
	)
	assert response.status_code == 401
	
def test_delete_note(set_up_new_note):
	token, note_id = set_up_new_note 
	response = client.delete(
		"/notes", params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["deleted"]

def test_delete_note_unauthorized(set_up_new_note):
	_, note_id = set_up_new_note 
	response = client.delete(
		"/notes", params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer ###"
		}
	)
	assert response.status_code == 401

def test_get_notes(set_up_new_note):
	token, note_id = set_up_new_note
	response = client.get(
		"/notes",
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["notes"][0]["id"] == note_id

def test_get_notes_unauthorized(set_up_new_note):
	response = client.get(
		"/notes",
		headers={
			"Authorization": f"Bearer ###"
		}
	)
	assert response.status_code == 401

def test_note_content_update(set_up_new_note):
	token, note_id = set_up_new_note
	new_content = "new note content"
	response = client.patch(
		"/notes", 
		json={"content": new_content},
		params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["updated"]["content"] == new_content
	
def test_note_content_update_unauthorized(set_up_new_note):
	_, note_id = set_up_new_note
	new_content = "new note content"
	response = client.patch(
		"/notes", 
		json={"content": new_content},
		params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer ##"
		}
	)
	assert response.status_code == 401

def test_note_update_archived_status(set_up_new_note):
	token, note_id = set_up_new_note
	response = client.patch(
		"/notes/archived", 
		params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["updated"]["is_archived"] == True
	response = client.patch(
		"/notes/archived", 
		params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["updated"]["is_archived"] == False

def test_note_update_archived_status_unauthorized(set_up_new_note):
	_, note_id = set_up_new_note
	response = client.patch(
		"/notes/archived", 
		params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer ###"
		}
	)
	assert response.status_code == 401

def test_get_note_categories_by_id(set_up_new_note):
	token, note_id = set_up_new_note
	response = client.get(
		"/notes/categories",
		params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["categories"][0]["name"] == "cat"
	

def test_get_note_categories_by_id_unauthorized(set_up_new_note):
	_, note_id = set_up_new_note
	response = client.get(
		"/notes/categories",
		params={"note_id": note_id},
		headers={
			"Authorization": f"Bearer ###"
		}
	)
	assert response.status_code == 401

def test_add_new_category(set_up_new_note):
	token, note_id = set_up_new_note
	new_name = "name"
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": new_name},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["added"]["name"] == new_name

def test_add_new_category_unauthorized(set_up_new_note):
	_, note_id = set_up_new_note
	new_name = "name"
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": new_name},
		headers={
			"Authorization": f"Bearer ###"
		}
	)
	assert response.status_code == 401

def test_delete_category_by_id(set_up_new_note):
	token, note_id = set_up_new_note
	new_name = "name"
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": new_name},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["added"]["name"] == new_name
	category_id = data["added"]["id"]
	response = client.delete(
		"/notes/categories",
		params={"category_id": category_id},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["deleted"]
	
def test_delete_category_by_id_unauthorized(set_up_new_note):
	token, note_id = set_up_new_note
	new_name = "name"
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": new_name},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["added"]["name"] == new_name
	category_id = data["added"]["id"]
	response = client.delete(
		"/notes/categories",
		params={"category_id": category_id},
		headers={
			"Authorization": f"Bearer ###"
		}
	)
	assert response.status_code == 401
 
def test_update_category_name_by_id(set_up_new_note):
	token, note_id = set_up_new_note
	new_name = "name"
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": new_name},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["added"]["name"] == new_name
	category_id = data["added"]["id"]
	new_name = "new name"
	response = client.patch(
		"/notes/categories",
		params={"category_id": category_id, "new_name": new_name},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["updated"]["name"] == new_name
	
def test_update_category_name_by_id_unauthorized(set_up_new_note):
	token, note_id = set_up_new_note
	new_name = "name"
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": new_name},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert data["added"]["name"] == new_name
	category_id = data["added"]["id"]
	new_name = "new name"
	response = client.patch(
		"/notes/categories",
		params={"category_id": category_id, "new_name": new_name},
		headers={
			"Authorization": f"Bearer ###"
		}
	)
	assert response.status_code == 401

def test_category_filter_by_name(set_up_new_note):
	token, note_id = set_up_new_note
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": "cat"},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert len(data["notes"]) == 1
	
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": "1"},
		headers={
			"Authorization": f"Bearer {token}"
		}
	)
	assert response.status_code == 200
	data = response.json()
	assert len(data["notes"]) == 0
	
def test_category_filter_by_name(set_up_new_note):
	_, note_id = set_up_new_note
	response = client.post(
		"/notes/categories",
		params={"note_id": note_id, "name": "cat"},
		headers={
			"Authorization": f"Bearer ###"
		}
	)
	assert response.status_code == 401
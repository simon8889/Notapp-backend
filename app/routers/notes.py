from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.dependencies import user_dependency
from app.schemas.NoteSchema import NoteSchema
from app.schemas.NoteContentSchema import NoteContentSchema
from app.services.NoteService import NoteService
from app.config.database import get_session

notes_router = APIRouter()

@notes_router.post("/")
def create_notes(user: user_dependency, note: NoteSchema, session=Depends(get_session)):
	new_note = NoteService(user["id"], session).create_note(note)
	return JSONResponse(status_code=status.HTTP_201_CREATED, content={"note": jsonable_encoder(new_note)})
	
@notes_router.get("/")
def get_notes(user: user_dependency, session=Depends(get_session)):
	notes = NoteService(user["id"], session).get_notes()
	return JSONResponse(status_code=status.HTTP_200_OK, content={"notes": jsonable_encoder(notes)})

@notes_router.delete("/")
def delete_note(user: user_dependency, note_id: int, session=Depends(get_session)):
	deleted_note = NoteService(user["id"], session).delete_note(note_id)
	if not deleted_note:
		return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"deleted": False})
	return JSONResponse(status_code=status.HTTP_200_OK, content={"deleted": True})

@notes_router.patch("/archived")
def change_note_archived_status(user: user_dependency, note_id: int, session=Depends(get_session)):
	updated_note = NoteService(user["id"], session).update_archived_status(note_id)
	if not updated_note:
		return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"updated": False})
	return JSONResponse(status_code=status.HTTP_200_OK, content={"updated": jsonable_encoder(updated_note)})

@notes_router.patch("/")
def change_note_content(user: user_dependency, note_id: int, content: NoteContentSchema, session=Depends(get_session)):
	updated_note = NoteService(user["id"], session).update_content(note_id, content.content)
	if not updated_note:
		return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"updated": False})
	return JSONResponse(status_code=status.HTTP_200_OK, content={"updated": jsonable_encoder(updated_note)})
	
@notes_router.get("/categories", tags=["category"])
def get_categories_by_note_id(user: user_dependency, note_id: int, session=Depends(get_session)):
	note_categories = NoteService(user["id"], session).get_note_categories_by_note_id(note_id)
	return JSONResponse(status_code=status.HTTP_200_OK, content={"categories": jsonable_encoder(note_categories)})

@notes_router.post("/categories", tags=["category"])
def add_category(user: user_dependency, note_id: int, name: str, session=Depends(get_session)):
	new_category = NoteService(user["id"], session).add_category(note_id, name)
	if not new_category:
		return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"added": False})
	return JSONResponse(status_code=status.HTTP_200_OK, content={"added": jsonable_encoder(new_category)})
	
@notes_router.delete("/categories", tags=["category"])
def delete_catergory_by_id(user: user_dependency, category_id: int, session=Depends(get_session)):
	category_to_delete = NoteService(user["id"], session).delete_category_by_category_id(category_id)
	if not category_to_delete:
		return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"deleted": False})
	return JSONResponse(status_code=status.HTTP_200_OK, content={"deleted": True})

@notes_router.patch("/categories", tags=["category"])
def update_category_name_by_id(user: user_dependency, category_id: int, new_name: str, session=Depends(get_session)):
	category_to_update = NoteService(user["id"], session).update_category_by_category_id(category_id, new_name)
	if not category_to_update:
		return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"updated": False})
	return JSONResponse(status_code=status.HTTP_200_OK, content={"updated": jsonable_encoder(category_to_update)})
	
@notes_router.get("/categories/filterbyname", tags=["category"])
def filter_notes_by_category(user: user_dependency, name: str, session=Depends(get_session)):
	notes_with_specific_category_name = NoteService(user["id"], session).get_categories_by_name(name)
	return JSONResponse(status_code=status.HTTP_200_OK, content={"notes": jsonable_encoder(notes_with_specific_category_name)})
	




	
	
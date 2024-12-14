from sqlmodel import Session, select, delete
from app.schemas.NoteSchema import NoteSchema
from app.models.NoteModel import Note, Category
from datetime import datetime, timezone

class NoteService:
	def __init__(self, user_id: int, db: Session):
		self.user_id = user_id
		self.db = db
	
	def convert_categorites(self, categories: list[str]) -> list[Category]:
		categories_list = []
		for name in categories:
			categories_list.append(Category(name=name))
		return categories_list
	
	def display_note_with_categories(self, note: Note):
		return {
			**note.model_dump(by_alias=True),
			'categories': [category.model_dump() for category in note.categories]
		} 
		

	def create_note(self, note: NoteSchema) -> Note:
		categories = self.convert_categorites(note.categories)
		new_note = Note(content=note.content,
				  		user_id=self.user_id,
						categories=categories)
		self.db.add(new_note)
		self.db.commit()
		self.db.refresh(new_note)
		return self.display_note_with_categories(new_note)
	
	def get_notes(self) -> list[Note]:
		query = select(Note).where(Note.user_id == self.user_id)
		result = self.db.exec(query).all()
		return [ self.display_note_with_categories(note) for note in result ]
		
	def get_note_by_id(self, note_id) -> Note | bool:
		query = select(Note).where(Note.id == note_id)
		result = self.db.exec(query).first()
		return result if result else False
		
	def delete_note(self, note_id: int) -> bool:
		note_to_delete = self.get_note_by_id(note_id)
		if not note_to_delete:
			return False
		self.delete_category_by_note_id(note_id)
		self.db.delete(note_to_delete)
		self.db.commit()
		return True
	
	def update_content(self, note_id: int, new_content: str) -> Note | bool:
		note_to_update = self.get_note_by_id(note_id)
		if not note_to_update:
			return False
		note_to_update.content = new_content 
		note_to_update.updated_at = datetime.now(timezone.utc)
		self.db.add(note_to_update)
		self.db.commit()
		self.db.refresh(note_to_update)
		return note_to_update
		
	def update_archived_status(self, note_id: int) -> Note | bool:
		note_to_update = self.get_note_by_id(note_id)
		if not note_to_update:
			return False
		note_to_update.is_archived = not note_to_update.is_archived
		self.db.add(note_to_update)
		self.db.commit()
		self.db.refresh(note_to_update)
		return note_to_update
	
	def get_note_categories_by_note_id(self, note_id: int) -> list[Category] | bool:
		note_to_get_categories = self.get_note_by_id(note_id)
		if not note_to_get_categories:
			return False
		return note_to_get_categories.categories
	
	def get_category_by_id(self, category_id: int) -> Category | bool:
		query = select(Category).where(Category.id == category_id)
		result = self.db.exec(query).first()
		return result if result else False
	
	def add_category(self, note_id : int, name: str) -> Category | bool:
		note_exists = self.get_note_by_id(note_id)
		if not note_exists:
			return False
		new_category = Category(note_id=note_id, name=name)
		self.db.add(new_category)
		self.db.commit()
		self.db.refresh(new_category)
		return new_category
	
	def delete_category_by_category_id(self, category_id: int) -> bool:
		category_to_delete = self.get_category_by_id(category_id)
		if not category_to_delete:
			return False
		self.db.delete(category_to_delete)
		self.db.commit()
		return True
	
	def delete_category_by_note_id(self, note_id: int): 
		query = delete(Category).where(Category.note_id == note_id)
		result = self.db.exec(query)
		self.db.commit()
	
	def update_category_by_category_id(self, category_id: int, new_name: str) -> Category | bool:
		category_to_update = self.get_category_by_id(category_id)
		if not category_to_update:
			return False
		category_to_update.name = new_name
		self.db.add(category_to_update)
		self.db.commit()
		self.db.refresh(category_to_update)
		return category_to_update
	
	def get_categories_by_name(self, name: str) -> list[Category]:
		user_notes = self.get_notes()
		user_notes_ids = [note["id"] for note in user_notes]
		query = select(Category.note_id).where(Category.name == name and Category.note_id in user_notes_ids)
		result = self.db.exec(query).unique().all()
		return [note for note in user_notes if note["id"] in result]
	

		
	
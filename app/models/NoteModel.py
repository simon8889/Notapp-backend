from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone

class Note(SQLModel, table=True):
	id: int | None = Field(default=None, primary_key=True)
	content: str
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
	updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
	is_archived: bool = False
	user_id: int | None = Field(default=None, foreign_key="user.id")
	categories: list["Category"] = Relationship(back_populates="note")
	
class Category(SQLModel, table=True):
	id: int | None = Field(default=None, primary_key=True)
	name: str
	note_id: int | None = Field(default=None, foreign_key="note.id")
	note: Optional[Note] = Relationship(back_populates="categories")



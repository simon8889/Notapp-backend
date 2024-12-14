from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

class NoteSchema(SQLModel):
	content: str
	categories: list[str]



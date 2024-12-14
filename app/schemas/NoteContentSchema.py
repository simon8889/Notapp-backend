from sqlmodel import SQLModel

class NoteContentSchema(SQLModel):
	content: str
	
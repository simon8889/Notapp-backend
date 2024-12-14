from sqlmodel import SQLModel

class UserSchema(SQLModel):
	username: str
	password: str
	
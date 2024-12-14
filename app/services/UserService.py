from sqlmodel import Session, select
from app.utils.hash_password import hash_password, verify_password
from app.schemas.UserSchema import UserSchema
from app.models.UserModel import User

class UserService:
	def __init__(self, user: UserSchema, db: Session):
		self.user = user
		self.db = db
		
	def create_user(self) -> int:
		valid_username_and_password = len(self.user.username) > 0 and len(self.user.password) > 0
		if not self.username_is_avalaible() or not valid_username_and_password:
			return False
		new_user = User(username=self.user.username,
						password=hash_password(self.user.password))
		self.db.add(new_user)
		self.db.commit()
		return True
		
	def username_is_avalaible(self) -> bool:
		query = select(User).where(User.username == self.user.username)
		result = self.db.exec(query).first()
		return False if result else True
		
	def authenticate_user(self) -> bool | User:
		query = select(User).where(User.username == self.user.username)
		user = self.db.exec(query).first()
		if user and verify_password(self.user.password, user.password):
			return user
		return False
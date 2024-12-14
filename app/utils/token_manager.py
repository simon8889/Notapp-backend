from fastapi import HTTPException, status, Depends 
from typing import Annotated
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from os import environ 
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = environ.get("JWT_SECRET_KEY")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="users/login")

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
	encode = {"sub": username, "id": user_id}
	expires = datetime.now(timezone.utc) + expires_delta
	encode.update({"exp": expires})
	return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		username: str = payload.get("sub")
		user_id: int = payload.get("id")
		if username is None or user_id is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
								detail="Could not validate user.")
		return {"username": username, "id": user_id}
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
							detail="Could not validate user.")
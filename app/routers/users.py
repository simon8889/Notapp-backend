from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse 
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.schemas.UserSchema import UserSchema
from app.config.database import get_session
from app.services.UserService import UserService
from app.schemas.Token import Token
from datetime import timedelta
from app.utils.token_manager import create_access_token

users_router = APIRouter()

@users_router.post("/create")
def create_user(user: UserSchema, session=Depends(get_session)):
	user_is_created = UserService(user, session).create_user()
	if not user_is_created:
		return JSONResponse(content="User not created", status_code=status.HTTP_306_RESERVED)
	return JSONResponse(content="User created", status_code=status.HTTP_201_CREATED)
		
@users_router.post("/login")
def login(user: Annotated[OAuth2PasswordRequestForm, Depends()], session=Depends(get_session)) -> Token:
	user_to_auth = UserSchema(username=user.username, password=user.password)
	authenticated = UserService(user_to_auth, session).authenticate_user()
	if not authenticated:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
	token = create_access_token(authenticated.username, authenticated.id, timedelta(minutes=30))
	return JSONResponse(status_code=status.HTTP_200_OK, content={"access_token": token, "token_type": "bearer", "username": authenticated.username})
from fastapi import Depends
from typing import Annotated
from app.utils.token_manager import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]



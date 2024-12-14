from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers.users import users_router
from app.routers.notes import notes_router
from .config.database import init_db
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
	init_db()
	yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(notes_router, prefix="/notes", tags=["notes"])

@app.get("/")
def health_check():
	return { "status": "Running" }
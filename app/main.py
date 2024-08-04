from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import auth, users
from db import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Opening database connection")
        database.init_db()
        yield
    except Exception as e:
        print(f"Error starting the application: {e}")
    finally:
        print("Closing database connection")
        database.close_db()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
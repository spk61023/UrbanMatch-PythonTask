from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///db.sqlite"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise e

def get_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Error getting session: {str(e)}")
        raise e
    finally:
        print("Session closed")
        db.close()

def close_db():
    try:
        engine.dispose()
    except Exception as e:
        print(f"Error closing database: {str(e)}")
        raise e
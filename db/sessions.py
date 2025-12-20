from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
# PostgreSQL
# engine = create_engine(
#     "postgresql+psycopg2://user:password@localhost/dbname"
# )

SessionLocal = sessionmaker(bind=engine)

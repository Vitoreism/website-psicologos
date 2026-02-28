from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:moskito@localhost:5432/postgres"


def connect_db():

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Erro: {e}")
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


DB_NAME = os.getenv("DB_NAME")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

if not all([DB_NAME, USER, PASSWORD, HOST, PORT]):
    logger.error("Could not extract enviroment variables from .env")

DATABASE_URL = F"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

def run_setup_sql(engine: Engine) -> None:
    file_path = "C:/Users/vitor/OneDrive/elo-terapeutico/website-psicologos/data/setup.sql"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            sql_commands = [cmd.strip() for cmd in file.read().split(';') if cmd.strip()]

        with engine.connect() as conn:
            for i in range(len(sql_commands)):
                print(sql_commands[i])
                conn.execute(text(sql_commands[i]))
            conn.commit()


        logger.info("Tabelas sincronizadas")

    except Exception as e:
        logger.error(f"Could not execute create table code. Error: {e}")

def connect_db() -> Engine:

    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))
        logger.info("CONECTADO")

        run_setup_sql(engine)
        return engine
    except Exception as e:
        logger.warning(f"Error in connecting with the database or it does not exist yet: {e}")
        
        try:
            logger.info(f"Creating a new database with name {DB_NAME}... ")
            url = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/postgres" # URL padrao
            temp_engine = create_engine(url, isolation_level="AUTOCOMMIT") # AUTOCOMMIT só é recomendado para conexões temporárias, que é o caso
            with temp_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE {DB_NAME}"))

            logger.info(f"Database {DB_NAME} created")
            temp_engine.dispose() # Desliga a engine temporários (Desligar engine != encerrar conexão)
            engine = create_engine(DATABASE_URL)

            run_setup_sql(engine)

            return engine
        except Exception as e:
            logger.error(f"Error in creating new database: {e}")

if __name__ == '__main__':
    ...
    
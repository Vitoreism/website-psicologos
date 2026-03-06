import logging 
from sqlalchemy import text
from sqlalchemy.engine import Engine
from typing import Dict
from data.database import connect_db


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class PsicologoManager:

    def __init__(self, engine: Engine, tabela: str) -> None:
        self.engine = engine 
        self.tabela = tabela

        logger.info("Psicologo Manager object created")

    def criar_psicologo(self, primeiro_nome: str, ultimo_name: str, email: str, senha: str) -> Dict:
        senha_hash = 'senhateste123'
        # Antes da query

        query = text(f"""
        INSERT INTO {self.tabela} (primeiro_nome, ultimo_nome, email, senha_hash)
        VALUES (:primeiro_nome, :ultimo_nome, :email, :senha_hash)
        RETURNING id;
        """
        )

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "primeiro_nome": primeiro_nome,
                    "ultimo_nome": ultimo_name,
                    "email": email,
                    "senha_hash": senha_hash
                })
                conn.commit()
                id = result.scalar()

                logger.info("New psicologo added")
                return id
        except Exception as e:
            logger.error(f"Error in creating new psicologo: {e}")
            return None



if __name__ == "__main__":
    ps_manager = PsicologoManager(engine=connect_db(), tabela='psicologos')
    ps_manager.criar_psicologo(primeiro_nome='Laura', ultimo_name='Nogueira', email='laura@gmail.com', senha='Genrolindo123')
    print(ps_manager)
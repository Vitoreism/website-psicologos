import logging 
from sqlalchemy import text
from sqlalchemy.engine import Engine
from typing import Any, Dict, List, Optional, Union
from data.database import connect_db
from utils.security import Security
from schemas.paciente_schemas import PacienteBase, PacienteCreate, PacienteUpdate,PacienteResponse



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class PacienteManager:

    def __init__(self, engine: Engine, tabela: str) -> None:
        self.engine = engine 
        self.tabela = tabela 

        logger.info("Paciente manager object created")

    def criar_paciente(self, paciente: PacienteCreate) -> int | None:
        senha_hash = Security.hash_password(paciente.senha)

        query= text(f"""
                    INSERT INTO {self.tabela} (primeiro_nome, ultimo_nome, email, senha_hash)
                    VALUES (:primeiro_nome, :ultimo_nome, :email, :senha_hash)
                    RETURNING id;
                    """
                    )
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query,{
                    "primeiro_nome": paciente.primeiro_nome,
                    "ultimo_nome": paciente.ultimo_nome,
                    "email": paciente.email,
                    "senha_hash": senha_hash
                })
                conn.commit()
                id  = result.scalar()

                logger.info("New paciente added")
                return id
        
        except Exception as e:
            logger.error(f"Error in creating new paciente: {e}")
            return None
    
    def read_pacientes(self) -> List[PacienteResponse]:
        query = text(f"SELECT id, primeiro_nome, ultimo_nome, email FROM {self.tabela}")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query)
                data = result.mappings().all()
            logger.info("Select made with succes")
            pacientes_seguros = [PacienteResponse(**row) for row in data]
            return pacientes_seguros
        except Exception as e:
            logger.error(e)
            return []
    

    def update_paciente(self, paciente_id: int, dados_novos: PacienteUpdate) -> bool:
        update_data = dados_novos.model_dump(exclude_unset=True)

        if not update_data:
            return False  

        set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        
        query = text(f"UPDATE {self.tabela} SET {set_clause} WHERE id = :id")
        
        params = {**update_data, "id": paciente_id}

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                conn.commit()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Erro no update parcial do paciente {paciente_id}: {e}")
            return False

    def buscar_por_id(self, id: Union[int, str]) -> Optional[PacienteResponse]:
        query = text(
            f"SELECT id, primeiro_nome, ultimo_nome, email FROM {self.tabela} WHERE id = :id"
        )

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"id": int(id)})
                row = result.mappings().first()

                if row is None:
                    logger.warning(f"Nenhum paciente encontrado com ID {id}.")
                    return None
                
                return PacienteResponse(**row)
                
        except Exception as e:
            logger.error(f"Erro ao buscar paciente com ID {id}: {e}")
            return None 

    def delete_paciente(self, paciente_id: int) -> bool:
        """
        Remove um paciente do banco de dados permanentemente usando o ID.
        Retorna True se a remoção foi bem-sucedida, False se o ID não existia.
        """
        query = text(f"DELETE FROM {self.tabela} WHERE id = :id")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"id": int(paciente_id)})
                
                conn.commit()
                
                if result.rowcount > 0:
                    logger.info(f"Paciente ID {paciente_id} deletado com sucesso.")
                    return True
                else:
                    logger.warning(f"Tentativa de deletar ID {paciente_id} que não existe.")
                    return False
                    
        except Exception as e:
            logger.error(f"Erro ao deletar paciente ID {paciente_id}: {e}")
            return False


if __name__ == '__main__':
    pac_manager = PacienteManager(engine=connect_db(), tabela='pacientes')

    
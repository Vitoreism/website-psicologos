import logging 
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from typing import Any, Dict, List, Optional, Union
from data.database import connect_db
from schemas.paciente_schemas import PacienteBase, PacienteCreate, PacienteUpdate, PacienteResponse



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

    def criar_paciente(self, paciente: PacienteCreate, id_psicologo: int) -> int | None:
        check_query = text(f"SELECT id_paciente, is_ativo FROM {self.tabela} WHERE id_psicologo = :id_psicologo AND email = :email")
        
        try:
            with self.engine.connect() as conn:
                # 1. Checa se já existe
                check_result = conn.execute(check_query, {"id_psicologo": id_psicologo, "email": paciente.email}).first()
                
                if check_result:
                    id_paciente, is_ativo = check_result
                    
                    if not is_ativo:
                        # 2. Se existe e está inativo, nós reativamos e atualizamos os dados
                        update_query = text(f"""
                            UPDATE {self.tabela} 
                            SET is_ativo = TRUE, primeiro_nome = :primeiro_nome, ultimo_nome = :ultimo_nome
                            WHERE id_paciente = :id_paciente
                        """)
                        conn.execute(update_query, {
                            "primeiro_nome": paciente.primeiro_nome,
                            "ultimo_nome": paciente.ultimo_nome,
                            "id_paciente": id_paciente
                        })
                        conn.commit()
                        logger.info(f"Paciente reativado. ID: {id_paciente}")
                        return id_paciente
                    else:
                        raise IntegrityError("O paciente já está cadastrado e ativo.", params={}, orig=Exception("Email duplicado"))

                # 3. Se não existe, cria um novo do zero
                insert_query = text(f"""
                            INSERT INTO {self.tabela} (id_psicologo, primeiro_nome, ultimo_nome, email, is_ativo)
                            VALUES (:id_psicologo, :primeiro_nome, :ultimo_nome, :email, :is_ativo)
                            RETURNING id_paciente;
                            """)
                
                result = conn.execute(insert_query, {
                    "id_psicologo": id_psicologo,
                    "primeiro_nome": paciente.primeiro_nome,
                    "ultimo_nome": paciente.ultimo_nome,
                    "email": paciente.email,
                    "is_ativo": True
                })
                conn.commit()
                id_paciente  = result.scalar()

                logger.info("Novo paciente adicionado.")
                return id_paciente
        
        except IntegrityError as e:
            logger.warning(f"Violação de unicidade ou paciente já existe: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao criar paciente: {e}")
            return None
    
    def read_pacientes(self, id_psicologo: int) -> List[PacienteResponse]:
        query = text(f"SELECT id_paciente, id_psicologo, primeiro_nome, ultimo_nome, email, is_ativo FROM {self.tabela} WHERE id_psicologo = :id_psicologo AND is_ativo = TRUE")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"id_psicologo": id_psicologo})
                data = result.mappings().all()
            logger.info("Leitura de pacientes concluída.")
            pacientes_seguros = [PacienteResponse(**row) for row in data]
            return pacientes_seguros
        except Exception as e:
            logger.error(f"Erro ao ler pacientes: {e}")
            return []
    

    def update_paciente(self, paciente_id: int, id_psicologo: int, dados_novos: PacienteUpdate) -> bool:
        update_data = dados_novos.model_dump(exclude_unset=True)

        if not update_data:
            return False  

        set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        
        query = text(f"UPDATE {self.tabela} SET {set_clause} WHERE id_paciente = :id_paciente AND id_psicologo = :id_psicologo")
        
        params = {**update_data, "id_paciente": paciente_id, "id_psicologo": id_psicologo}

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, params)
                conn.commit()
                return result.rowcount > 0
        except IntegrityError as e:
            logger.warning(f"Erro de integridade ao atualizar paciente {paciente_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro no update parcial do paciente {paciente_id}: {e}")
            return False

    def buscar_por_id(self, id: Union[int, str], id_psicologo: int) -> Optional[PacienteResponse]:
        query = text(
            f"SELECT id_paciente, id_psicologo, primeiro_nome, ultimo_nome, email, is_ativo FROM {self.tabela} WHERE id_paciente = :id_paciente AND id_psicologo = :id_psicologo"
        )

        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"id_paciente": int(id), "id_psicologo": id_psicologo})
                row = result.mappings().first()

                if row is None:
                    logger.warning(f"Nenhum paciente encontrado com ID {id} para este psicólogo.")
                    return None
                
                return PacienteResponse(**row)
                
        except Exception as e:
            logger.error(f"Erro ao buscar paciente com ID {id}: {e}")
            return None 

    def delete_paciente(self, paciente_id: int, id_psicologo: int) -> bool:
        """
        Desativa um paciente no banco de dados (Soft Delete) usando o ID_PACIENTE e ID_PSICOLOGO.
        Altera a coluna is_ativo para FALSE.
        """
        query = text(f"UPDATE {self.tabela} SET is_ativo = FALSE WHERE id_paciente = :id_paciente AND id_psicologo = :id_psicologo")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"id_paciente": int(paciente_id), "id_psicologo": id_psicologo})
                
                conn.commit()
                
                if result.rowcount > 0:
                    logger.info(f"Paciente ID {paciente_id} desativado com sucesso.")
                    return True
                else:
                    logger.warning(f"Tentativa de desativar ID {paciente_id} que não existe ou pertence a outro psicólogo.")
                    return False
                    
        except Exception as e:
            logger.error(f"Erro ao desativar paciente ID {paciente_id}: {e}")
            return False


if __name__ == '__main__':
    pac_manager = PacienteManager(engine=connect_db(), tabela='pacientes')

    #print(pac_manager.criar_paciente(paciente=PacienteCreate(primeiro_nome="João", ultimo_nome="Silva", email="vasco@gmail.com"), id_psicologo=1))
    print(pac_manager.read_pacientes(id_psicologo=1))
    print(pac_manager.delete_paciente(paciente_id=1, id_psicologo=1))
    print(pac_manager.read_pacientes(id_psicologo=1))
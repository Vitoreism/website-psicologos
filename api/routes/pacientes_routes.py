from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from sqlalchemy.exc import IntegrityError
from schemas.paciente_schemas import PacienteCreate, PacienteResponse, PacienteUpdate
from managers.paciente import PacienteManager
from data.database import connect_db
from utils.auth import get_current_psicologo
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_paciente_manager():
    engine = connect_db()
    return PacienteManager(engine=engine, tabela="pacientes")

@router.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_paciente(
    paciente_in: PacienteCreate, 
    id_psicologo_logado: int = Depends(get_current_psicologo),
    manager: PacienteManager = Depends(get_paciente_manager)
):
    try:
        paciente_id = manager.criar_paciente(paciente_in, id_psicologo_logado)
        if not paciente_id:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao cadastrar paciente."
            )
        return {"mensagem": "Paciente cadastrado com sucesso", "id": paciente_id}
    except IntegrityError as e:
        msg = str(e) if str(e) else "Já existe um paciente cadastrado com este e-mail."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg
        )

@router.get("/", response_model=List[PacienteResponse])
def listar_pacientes(
    id_psicologo_logado: int = Depends(get_current_psicologo),
    manager: PacienteManager = Depends(get_paciente_manager)
):
    return manager.read_pacientes(id_psicologo_logado)

@router.get("/{paciente_id}", response_model=PacienteResponse)
def buscar_paciente(
    paciente_id: int, 
    id_psicologo_logado: int = Depends(get_current_psicologo),
    manager: PacienteManager = Depends(get_paciente_manager)
):
    paciente = manager.buscar_por_id(paciente_id, id_psicologo_logado)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return paciente

@router.put("/{paciente_id}")
def atualizar_paciente(
    paciente_id: int, 
    dados_novos: PacienteUpdate,
    id_psicologo_logado: int = Depends(get_current_psicologo),
    manager: PacienteManager = Depends(get_paciente_manager)
):
    try:
        sucesso = manager.update_paciente(paciente_id, id_psicologo_logado, dados_novos)
        if not sucesso:
             raise HTTPException(status_code=404, detail="Paciente não encontrado ou sem alterações.")
        return {"mensagem": "Paciente atualizado com sucesso"}
    except IntegrityError:
        raise HTTPException(status_code=409, detail="E-mail já está em uso por outro paciente.")

@router.delete("/{paciente_id}")
def deletar_paciente(
    paciente_id: int, 
    id_psicologo_logado: int = Depends(get_current_psicologo),
    manager: PacienteManager = Depends(get_paciente_manager)
):
    sucesso = manager.delete_paciente(paciente_id, id_psicologo_logado)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return {"mensagem": "Paciente desativado com sucesso"}

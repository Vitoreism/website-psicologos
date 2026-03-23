from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError
from schemas.psicologo_schemas import PsicologoCreate, PsicologoResponse
from managers.psicologo import PsicologoManager
from data.database import connect_db
from typing import Dict

router = APIRouter()

# Função de Dependência para fornecer o Manager às rotas
def get_psico_manager():
    engine = connect_db()
    return PsicologoManager(engine=engine, tabela="psicologos")

@router.post("/", response_model=PsicologoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_psicologo(
    psico_in: PsicologoCreate, 
    manager: PsicologoManager = Depends(get_psico_manager)
):
    try:
        psico_criado_dict = manager.criar_psicologo(psico_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um psicólogo cadastrado com este e-mail ou CRP."
        )

    if not psico_criado_dict:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao cadastrar psicólogo. Tente novamente mais tarde."
        )

    # O FastAPI pega esse dicionário e valida contra o PsicologoResponse automaticamente
    return psico_criado_dict
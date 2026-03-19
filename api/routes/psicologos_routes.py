from fastapi import APIRouter, HTTPException, status, Depends
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
    psico_criado_dict = manager.criar_psicologo(psico_in)
    
    if not psico_criado_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível realizar o cadastro. Verifique se o E-mail ou CRP já estão em uso."
        )

    # O FastAPI pega esse dicionário e valida contra o PsicologoResponse automaticamente
    return psico_criado_dict
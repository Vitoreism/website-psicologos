from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import psicologos_routes, agendamentos_routes
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse



app = FastAPI(
    title="API Elo Terapêutico",
    description="Backend para gestão de clínicas, psicólogos e pacientes.",
    version="1.0.0"
)

# 2. Configuração de CORS (Essencial para o Front-end conseguir conversar com a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, você troca o "*" pela URL real do seu site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    psicologos_routes.router,
    prefix="/api/psicologos",
    tags=["Psicólogos"]
)

app.include_router(
    agendamentos_routes.router,
    prefix="/api/agendamentos",
    tags=["Agendamentos e Calendário Google"]
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros_formatados = []
    
    for error in exc.errors():
        # Limpa a mensagem retirando o prefixo padrão do Pydantic
        mensagem_limpa = error.get("msg").replace("Value error, ", "")
        
        # Pega o último item da localização (ex: 'senha', 'email')
        campo = error.get("loc")[-1] if error.get("loc") else "desconhecido"
        
        erros_formatados.append({
            "campo": campo,
            "mensagem": mensagem_limpa
        })

    # Retorna o JSON limpo que você tinha antes!
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "erro": "Erro de validação nos dados enviados.",
            "detalhes": erros_formatados
        },
    )


# 4. Rota raiz (Health Check)
@app.get("/", tags=["Status"])
def health_check():
    return {
        "status": "online",
        "projeto": "Elo Terapêutico",
        "documentacao": "Acesse http://127.0.0.1:8000/docs"
    }
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import psicologos_routes

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

# 4. Rota raiz (Health Check)
@app.get("/", tags=["Status"])
def health_check():
    return {
        "status": "online",
        "projeto": "Elo Terapêutico",
        "documentacao": "Acesse http://127.0.0.1:8000/docs"
    }
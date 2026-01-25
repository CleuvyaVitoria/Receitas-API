from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db, close_db

from app.routes.usuario import router as usuario_router
from app.routes.ingrediente import router as ingrediente_router
from app.routes.receita import router as receita_router

from fastapi_pagination import add_pagination


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Banco de dados conectado")
    yield
    await close_db()
    print("Banco de dados desconectado")


app = FastAPI(
    title="API de Receitas",
    version="1.0.0",
    description="API para gerenciamento de usuários, receitas e ingredientes",
    lifespan=lifespan
)

app.include_router(usuario_router)
app.include_router(ingrediente_router)
app.include_router(receita_router)


@app.get("/")
async def root():
    return {"message": "API de Receitas rodando"}

add_pagination(app)
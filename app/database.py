import os
import logging
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from beanie import init_beanie

from app.models import Usuario, Receita, Ingrediente

# Carrega as variáveis do .env
load_dotenv()

# Variáveis de ambiente
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

# Cliente global
_client: AsyncMongoClient | None = None


async def init_db():
    global _client

    if not MONGODB_URI or not MONGODB_DB:
        logger.error("Variáveis MONGODB_URI ou MONGODB_DB não encontradas no .env")
        raise RuntimeError("Configuração do banco inválida")

    try:
        _client = AsyncMongoClient(MONGODB_URI)
        database = _client[MONGODB_DB]

        await init_beanie(
            database=database,
            document_models=[
                Usuario,
                Receita,
                Ingrediente
            ],
        )

        logger.info(f"Beanie conectado ao banco: {MONGODB_DB}")

    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        raise


async def close_db():
    global _client

    if _client is not None:
        _client.close()
        logger.info("Conexão com MongoDB encerrada")
        _client = None

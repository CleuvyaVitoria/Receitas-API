from pydantic import BaseModel, Field, ConfigDict
from beanie.odm.fields import PydanticObjectId



# ================= USUÁRIO =================

class UsuarioCreate(BaseModel):
    nome: str
    email: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None



# ================= INGREDIENTE =================

class IngredienteCreate(BaseModel):
    nome: str
    unidade_medida: str | None = None


class IngredienteUpdate(BaseModel):
    nome: str | None = None
    unidade_medida: str | None = None



# ================= RECEITA =================

class ReceitaCreate(BaseModel):
    titulo: str
    descricao: str
    usuario_id: PydanticObjectId
    ingredientes_ids: list[PydanticObjectId] = Field(default_factory=list)


class ReceitaUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    ingredientes_ids: list[PydanticObjectId] | None = None


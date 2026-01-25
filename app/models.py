from beanie import Document, Link
from pydantic import Field



# ================= USUÁRIO =================

class Usuario(Document):
    nome: str
    email: str

    class Settings:
        name = "usuarios"


# ================= INGREDIENTE =================

class Ingrediente(Document):
    nome: str
    unidade_medida: str | None = Field(
        default=None,
        description="Ex: g, ml, unidade"
    )

    class Settings:
        name = "ingredientes"


# ================= RECEITA =================

class Receita(Document):
    titulo: str
    descricao: str
    usuario: Link[Usuario]
    ingredientes: list[Link[Ingrediente]] = Field(default_factory=list)

    class Settings:
        name = "receitas"

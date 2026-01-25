from fastapi import APIRouter, HTTPException, status
from beanie.odm.fields import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import paginate

from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

#         CRIAR USUARIO 
@router.post(
    "/",
    response_model=Usuario,
    status_code=status.HTTP_201_CREATED
)
async def criar_usuario(data: UsuarioCreate):
    usuario = Usuario(
        nome=data.nome,
        email=data.email
    )
    await usuario.insert()
    return usuario

#  LISTAR USUARIO COM PAGINAÇÃO
@router.get(
    "/",
    response_model=Page[Usuario]
)
async def listar_usuarios() -> Page[Usuario]:
    return await paginate(Usuario.find_all())


# BUSCAR USUARIO POR ID
@router.get(
    "/{usuario_id}",
    response_model=Usuario
)
async def obter_usuario(usuario_id: PydanticObjectId) -> Usuario:
    usuario = await Usuario.get(usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return usuario


# ATUALIZAR USUARIO
@router.put(
    "/{usuario_id}",
    response_model=Usuario
)
async def atualizar_usuario(
    usuario_id: PydanticObjectId,
    data: UsuarioUpdate
):
    usuario = await Usuario.get(usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    update_data = data.model_dump(exclude_unset=True)

    for campo, valor in update_data.items():
        setattr(usuario, campo, valor)

    await usuario.save()
    return usuario

# DELETAR USUARIO
@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deletar_usuario(usuario_id: PydanticObjectId):
    usuario = await Usuario.get(usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    await usuario.delete()

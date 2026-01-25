from fastapi import APIRouter, HTTPException, status
from beanie.odm.fields import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import paginate

from app.models import Ingrediente
from app.schemas import IngredienteCreate, IngredienteUpdate


router = APIRouter(
    prefix="/ingredientes",
    tags=["Ingredientes"]
)

# CRIAR INGREDIENTE - POST
@router.post(
    "/",
    response_model=Ingrediente,
    status_code=status.HTTP_201_CREATED
)
async def criar_ingrediente(data: IngredienteCreate):
    ingrediente = Ingrediente(
        nome=data.nome,
        unidade_medida=data.unidade_medida
    )

    await ingrediente.insert()
    return ingrediente



#  LISTAR INGREDIENTES COM PAGINAÇÃO
@router.get(
    "/",
    response_model=Page[Ingrediente]
)
async def listar_ingredientes() -> Page[Ingrediente]:
    return await paginate(Ingrediente.find_all())


#    LISTAR INGREDIENTE POR ID
@router.get(
    "/{ingrediente_id}",
    response_model=Ingrediente
)
async def obter_ingrediente(
    ingrediente_id: PydanticObjectId
) -> Ingrediente:
    ingrediente = await Ingrediente.get(ingrediente_id)

    if not ingrediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente não encontrado"
        )

    return ingrediente



#    ATUALIZAR INGREDIENTE
@router.put(
    "/{ingrediente_id}",
    response_model=Ingrediente
)
async def atualizar_ingrediente(
    ingrediente_id: PydanticObjectId,
    data: IngredienteUpdate
):
    ingrediente = await Ingrediente.get(ingrediente_id)

    if not ingrediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente não encontrado"
        )

    update_data = data.model_dump(exclude_unset=True)

    for campo, valor in update_data.items():
        setattr(ingrediente, campo, valor)

    await ingrediente.save()
    return ingrediente


# DELETAR INGREDIENTE 
@router.delete(
    "/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deletar_ingrediente(ingrediente_id: PydanticObjectId):
    ingrediente = await Ingrediente.get(ingrediente_id)

    if not ingrediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente não encontrado"
        )

    await ingrediente.delete()

from fastapi import APIRouter, HTTPException, status, Query
from beanie.odm.fields import PydanticObjectId
from fastapi_pagination import Page
from fastapi_pagination.ext.beanie import paginate, apaginate
from beanie import PydanticObjectId
from beanie.operators import In, RegEx
from bson import ObjectId


from app.models import Receita, Usuario, Ingrediente
from app.schemas import ReceitaCreate, ReceitaUpdate

router = APIRouter(
    prefix="/receitas",
    tags=["Receitas"]
)



#         CRIAR RECEITA - POST
@router.post("/", response_model=Receita, status_code=201)
async def criar_receita(data: ReceitaCreate):
    """
    Cria uma nova receita associada a um usuário e a uma lista de ingredientes.

    Valida a existência do usuário e dos ingredientes antes de salvar.
    
    Retorna a receita criada com os dados relacionados.
    """

    # --- usuário ---
    usuario = await Usuario.get(data.usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=404, detail="Usuário não encontrado"
        )

    # --- ingredientes ---
    ingredientes = []
    if data.ingredientes_ids:
        ingredientes = await Ingrediente.find(In(Ingrediente.id, data.ingredientes_ids)).to_list()

        if len(ingredientes) != len(data.ingredientes_ids):
            raise HTTPException(
                status_code=404, detail="Um ou mais ingredientes não foram encontrados"
            )

    receita = Receita(
        titulo=data.titulo,
        descricao=data.descricao,
        usuario=usuario,
        ingredientes=ingredientes
    )

    await receita.insert()
    await receita.fetch_all_links()
    return receita




#       LISTAR RECEITAS - PAGINAÇÃO  ( ajustado o uso do for)
@router.get("/", response_model=Page[Receita])
async def listar_receitas() -> Page[Receita]:
    """
    Lista todas as receitas cadastradas de forma paginada.

    Retorna as receitas.
    """
    # O fetch_links=True faz o trabalho do seu loop automaticamente
    return await paginate(Receita.find(fetch_links=True))




#      BUSCAR POR TITULO
@router.get("/buscar_titulo")
async def buscar_receitas(palavra: str = Query(..., description="Palavra para buscar no título")):
    """
    Busca receitas cujo título contenha a palavra informada.

    A busca é case-insensitive.
    """
    receitas = await Receita.find(
        RegEx(Receita.titulo, palavra, "i")  # "i" = case-insensitive
    ).to_list()
    
    return receitas



#           CONTAGEM DE RECEITAS
## CONTA AS RECEITAS POR USUARIO E ORDENA QUAL USUARIO TEM MAIS
@router.get("/estatisticas/contagem-por-usuario")
async def contar_receitas_por_usuario(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """
    Retorna a quantidade de receitas por usuário; o usuário só aparecerá caso possua alguma receita.

    Os resultados são ordenados do usuário com mais receitas para o com menos.
    
    A resposta é paginada manualmente.
    """
    skip = (page - 1) * size

    pipeline = [
        {
            "$group": {
                "_id": "$usuario.$id",
                "total_receitas": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_receitas": -1}  # quem tem mais receitas primeiro
        },
        {
            "$lookup": {
                "from": "usuarios",   
                "localField": "_id",
                "foreignField": "_id",
                "as": "usuario"
            }
        },
        {"$unwind": "$usuario"},
        {
            "$project": {
                "_id": 0,
                "usuario_id": {"$toString": "$_id"},
                "nome": "$usuario.nome",
                "email": "$usuario.email",
                "total_receitas": 1
            }
        },
        {"$skip": skip},
        {"$limit": size}
    ]

    return await Receita.aggregate(pipeline).to_list()



#       LISTAR RECEITA POR ID- (professor em tags,usa fetch sim, VERIFICAR). 
#       Consegue trazer todos os dados, tanto do cliente como os do ingrediente 
#
@router.get("/{receita_id}", response_model=Receita)
async def obter_receita(receita_id: PydanticObjectId) -> Receita:
    """
    Busca uma receita pelo seu ID.

    Retorna a receita com os dados completos do usuário e dos ingredientes.
    """
    # O fetch_links=True busca a receita e todos os links (usuario, ingredientes) de uma só vez
    receita = await Receita.get(receita_id, fetch_links=True)

    if not receita:
        raise HTTPException(status_code=404, detail="Receita não encontrada")

    return receita



# ATUALIZAR RECEITA
@router.put("/{receita_id}", response_model=Receita)
async def atualizar_receita(receita_id: PydanticObjectId, data: ReceitaUpdate) -> Receita:
    """
    Atualiza os dados de uma receita existente.

    Permite alterar título, descrição e ingredientes.
    
    Retorna a receita atualizada.
    """
    # Busca a receita original
    receita = await Receita.get(receita_id)
    if not receita:
        raise HTTPException(status_code=404, detail="Receita não encontrada")

    #  Converte o schema em dicionário filtrando apenas o que foi enviado
    update_data = data.model_dump(exclude_unset=True)

    #(Converte IDs em Objetos)
    if "ingredientes_ids" in update_data:
        ids = update_data.pop("ingredientes_ids")
        ingredientes = await Ingrediente.find({"_id": {"$in": ids}}).to_list()
        
        if len(ingredientes) != len(ids):
             raise HTTPException(status_code=400, detail="Um ou mais IDs de ingredientes são inválidos")
        
        receita.ingredientes = ingredientes

    #Loop (Igual ao do seu professor)
    for key, value in update_data.items():
        setattr(receita, key, value)

    #Salva e garante que os links apareçam no retorno
    await receita.save()
    await receita.fetch_all_links() 
    
    return receita


#               DELETA
@router.delete("/{receita_id}")
async def deletar_receita(receita_id: PydanticObjectId) -> dict:
    """
    Remove uma receita do banco de dados pelo seu ID.

    Retorna uma mensagem de confirmação após a exclusão.
    """
    receita = await Receita.get(receita_id)
    
    if not receita:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    
    await receita.delete()
    return {"message": "Receita deletada"}

from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field


class ExtractSQLQuery(BaseModel):
    """
    Cuando un usuario quiere información de productos que son platillos como precio, descripcion, existencia, etc.
    Debes usar esta herramienta que extrae una consulta SQL de una conversacion para buscar en una base de datos informacion de productos en la tabla de products.
    """

    sql_query: str = Field(..., description="Consulta SQL")


class ExtractVectorDBQuery(BaseModel):
    """
    Cuando un cliente pide alguna recomendación sobre platillos o quiere saber si hay platillos con ciertos ingredientes
    debes de extraer algo dicho por el cliente como una pregunta, frase, etc. es para buscar en una base de datos de vectores por similaridad, debe ser algo genérico sobre
    productos como recomendaciones en base a contenido, recomendaciones de platillos, si hay platillos de cierto
    tipo, platillos con o sin ciertos ingredientes para cierto tipo de personas.
    """

    vectordb_query: str = Field(..., description="Consulta extendida")


class AddOrderProduct(BaseModel):
    """
    Cuando un cliente quiere ordenar un platillo existente a su orden debes extraer
    """

    product: str = Field(..., description="Nombre del producto")
    quantity: str = Field(..., description="Cantidad del producto")


class DeleteOrderProduct(BaseModel):
    """
    Cuando un cliente diga que quiere eliminar un producto o platillo de su orden
    """

    products: List[str] = Field(...,
                                description="Lista de nombres de productos")


class ModifyOrderProduct(BaseModel):
    """
    Cuando un cliente diga que quiere modificar un producto o platillo de su orden cambiando la cantidad, debes de obtener los productos y cantidades correspondientes
    debe estar ordenados de modo que el primer producto corresponda a la primera cantidad, el segundo producto a la segunda cantidad y así sucesivamente.
    """

    products: List[str] = Field(..., description="Nombres de productos")
    quantities: List[str] = Field(..., description="Cantidades de productos")


class BuyOrder(BaseModel):
    """
    Cuando un cliente confirme su orden
    """

    pass

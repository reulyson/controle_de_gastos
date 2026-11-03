"""CRUD de categorias."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCategoria
from app.modulos.modelos import Categoria
from app.nucleo.banco import obter_sessao

roteador = APIRouter(prefix="/categorias", tags=["Categorias"])


class CategoriaCriar(BaseModel):
    """Payload de criação."""

    nome: str = Field(..., min_length=1, max_length=120)
    tipo: TipoCategoria


class CategoriaResposta(BaseModel):
    """Categoria persistida."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    tipo: str


@roteador.get("", response_model=list[CategoriaResposta])
def listar(sessao: Session = Depends(obter_sessao)) -> list[Categoria]:
    """Lista todas as categorias."""
    return list(sessao.scalars(select(Categoria)).all())


@roteador.post("", response_model=CategoriaResposta, status_code=201)
def criar(corpo: CategoriaCriar, sessao: Session = Depends(obter_sessao)) -> Categoria:
    """Cria categoria."""
    cat = Categoria(nome=corpo.nome, tipo=corpo.tipo.value)
    sessao.add(cat)
    sessao.commit()
    sessao.refresh(cat)
    return cat


@roteador.delete("/{categoria_id}", status_code=204)
def excluir(categoria_id: int, sessao: Session = Depends(obter_sessao)) -> None:
    """Remove categoria."""
    cat = sessao.get(Categoria, categoria_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    sessao.delete(cat)
    sessao.commit()

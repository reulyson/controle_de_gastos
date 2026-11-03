"""Tags como alias de categorias."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCategoria
from app.modulos.modelos import Categoria
from app.nucleo.banco import obter_sessao

roteador = APIRouter(prefix="/tags", tags=["Tags"])


class TagResposta(BaseModel):
    id: int
    nome: str


class TagCriar(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)


@roteador.get("", response_model=list[TagResposta])
def listar_tags(sessao: Session = Depends(obter_sessao)) -> list[TagResposta]:
    """Lista tags (categorias de receita e despesa)."""
    cats = sessao.scalars(
        select(Categoria).where(Categoria.tipo.in_([TipoCategoria.RECEITA.value, TipoCategoria.DESPESA.value]))
    ).all()
    return [TagResposta(id=c.id, nome=c.nome) for c in cats]


@roteador.post("", response_model=TagResposta, status_code=201)
def criar_tag(corpo: TagCriar, sessao: Session = Depends(obter_sessao)) -> TagResposta:
    """Cria tag como categoria de despesa."""
    cat = Categoria(nome=corpo.nome, tipo=TipoCategoria.DESPESA.value)
    sessao.add(cat)
    sessao.commit()
    sessao.refresh(cat)
    return TagResposta(id=cat.id, nome=cat.nome)

"""Tags como alias de categorias."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCategoria
from app.modulos.modelos import Categoria, Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_usuario_atual

roteador = APIRouter(prefix="/tags", tags=["Tags"])


class TagResposta(BaseModel):
    id: int
    nome: str


class TagCriar(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)


@roteador.get("", response_model=list[TagResposta])
def listar_tags(
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[TagResposta]:
    cats = sessao.scalars(
        select(Categoria).where(
            or_(Categoria.usuario_id.is_(None), Categoria.usuario_id == usuario.id)
        )
    ).all()
    return [TagResposta(id=c.id, nome=c.nome) for c in cats]


@roteador.post("", response_model=TagResposta, status_code=201)
def criar_tag(
    corpo: TagCriar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> TagResposta:
    cat = Categoria(
        nome=corpo.nome.strip(),
        tipo=TipoCategoria.AMBOS.value,
        usuario_id=usuario.id,
    )
    sessao.add(cat)
    sessao.commit()
    sessao.refresh(cat)
    return TagResposta(id=cat.id, nome=cat.nome)

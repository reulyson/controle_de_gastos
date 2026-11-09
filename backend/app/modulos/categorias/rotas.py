"""CRUD de categorias (sistema + pessoais do usuário)."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCategoria
from app.modulos.modelos import Categoria, Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_usuario_atual

roteador = APIRouter(prefix="/categorias", tags=["Categorias"])


class CategoriaCriar(BaseModel):
    """Payload de criação (sempre pessoal; tipo opcional legado)."""

    nome: str = Field(..., min_length=1, max_length=120)
    tipo: TipoCategoria | None = None


class CategoriaResposta(BaseModel):
    """Categoria persistida."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    tipo: str
    origem: str


def _para_resposta(cat: Categoria) -> CategoriaResposta:
    return CategoriaResposta(
        id=cat.id,
        nome=cat.nome,
        tipo=cat.tipo,
        origem=cat.origem,
    )


@roteador.get("", response_model=list[CategoriaResposta])
def listar(
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[CategoriaResposta]:
    """Lista categorias sistema + pessoais do usuário."""
    cats = list(
        sessao.scalars(
            select(Categoria).where(
                or_(Categoria.usuario_id.is_(None), Categoria.usuario_id == usuario.id)
            )
        ).all()
    )
    padrao = sorted(
        (c for c in cats if c.usuario_id is None),
        key=lambda c: c.nome.casefold(),
    )
    pessoal = sorted(
        (c for c in cats if c.usuario_id is not None),
        key=lambda c: c.nome.casefold(),
    )
    return [_para_resposta(c) for c in [*padrao, *pessoal]]


@roteador.post("", response_model=CategoriaResposta, status_code=201)
def criar(
    corpo: CategoriaCriar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> CategoriaResposta:
    """Cria categoria pessoal do usuário autenticado."""
    nome = corpo.nome.strip()
    if not nome:
        raise HTTPException(status_code=422, detail="Informe o nome da categoria")
    existe = sessao.scalar(
        select(Categoria).where(
            Categoria.nome == nome,
            Categoria.usuario_id == usuario.id,
        )
    )
    if existe is not None:
        raise HTTPException(status_code=409, detail="Categoria já cadastrada")
    cat = Categoria(
        nome=nome,
        tipo=TipoCategoria.AMBOS.value,
        usuario_id=usuario.id,
    )
    sessao.add(cat)
    sessao.commit()
    sessao.refresh(cat)
    return _para_resposta(cat)


@roteador.delete("/{categoria_id}", status_code=204)
def excluir(
    categoria_id: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> None:
    """Remove categoria pessoal; categorias sistema são protegidas."""
    cat = sessao.get(Categoria, categoria_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    if cat.usuario_id is None:
        raise HTTPException(
            status_code=403, detail="Categorias padrão do sistema não podem ser removidas"
        )
    if cat.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    sessao.delete(cat)
    sessao.commit()

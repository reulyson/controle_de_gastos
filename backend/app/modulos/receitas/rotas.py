"""CRUD de receitas."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.modelos import Receita, Usuario
from app.modulos.schemas_lancamento import (
    LancamentoAtualizarBase,
    LancamentoCriarBase,
    aplicar_atualizacao_lancamento,
    gerar_mensais_ao_criar,
)
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_carteira_do_usuario, obter_usuario_atual

roteador = APIRouter(prefix="/receitas", tags=["Receitas"])


class ReceitaCriar(LancamentoCriarBase):
    """Criação de receita."""


class ReceitaAtualizar(LancamentoAtualizarBase):
    """Atualização de receita."""


class ReceitaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    carteira_id: int
    descricao: str
    valor: Decimal
    categoria_id: int | None
    recorrencia: str
    valor_variavel: bool = False
    tipo: str = "receita"
    mes_referencia: int | None = None
    ano_referencia: int | None = None
    ativo: bool


def _resposta(r: Receita) -> ReceitaResposta:
    return ReceitaResposta(
        id=r.id,
        carteira_id=r.carteira_id,
        descricao=r.descricao,
        valor=r.valor,
        categoria_id=r.categoria_id,
        recorrencia=r.recorrencia,
        valor_variavel=bool(r.valor_variavel),
        ativo=r.ativo,
    )


@roteador.get("", response_model=list[ReceitaResposta])
def listar(
    carteira_id: int = Query(...),
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[ReceitaResposta]:
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    receitas = sessao.scalars(select(Receita).where(Receita.carteira_id == carteira_id)).all()
    return [_resposta(r) for r in receitas]


@roteador.post("", response_model=ReceitaResposta, status_code=201)
def criar(
    corpo: ReceitaCriar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> ReceitaResposta:
    obter_carteira_do_usuario(corpo.carteira_id, usuario, sessao)
    receita = Receita(
        carteira_id=corpo.carteira_id,
        descricao=corpo.descricao,
        valor=corpo.valor,
        categoria_id=corpo.categoria_id,
        recorrencia=corpo.recorrencia.value,
        valor_variavel=corpo.valor_variavel,
    )
    sessao.add(receita)
    sessao.commit()
    sessao.refresh(receita)
    gerar_mensais_ao_criar(
        sessao,
        tipo="receita",
        lancamento_id=receita.id,
        recorrencia=corpo.recorrencia,
        mes_referencia=corpo.mes_referencia,
        ano_referencia=corpo.ano_referencia,
        quantidade_meses=corpo.quantidade_meses,
    )
    return ReceitaResposta(
        id=receita.id,
        carteira_id=receita.carteira_id,
        descricao=receita.descricao,
        valor=receita.valor,
        categoria_id=receita.categoria_id,
        recorrencia=receita.recorrencia,
        valor_variavel=bool(receita.valor_variavel),
        mes_referencia=corpo.mes_referencia,
        ano_referencia=corpo.ano_referencia,
        ativo=receita.ativo,
    )


@roteador.get("/{receita_id}", response_model=ReceitaResposta)
def obter(
    receita_id: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> ReceitaResposta:
    receita = sessao.get(Receita, receita_id)
    if receita is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    obter_carteira_do_usuario(receita.carteira_id, usuario, sessao)
    return _resposta(receita)


@roteador.put("/{receita_id}", response_model=ReceitaResposta)
@roteador.patch("/{receita_id}", response_model=ReceitaResposta)
def atualizar(
    receita_id: int,
    corpo: ReceitaAtualizar,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> ReceitaResposta:
    receita = sessao.get(Receita, receita_id)
    if receita is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    obter_carteira_do_usuario(receita.carteira_id, usuario, sessao)
    aplicar_atualizacao_lancamento(
        entidade=receita,
        dados=corpo.model_dump(exclude_unset=True),
    )
    sessao.commit()
    sessao.refresh(receita)
    return _resposta(receita)


@roteador.delete("/{receita_id}", status_code=204)
def excluir(
    receita_id: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> None:
    receita = sessao.get(Receita, receita_id)
    if receita is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    obter_carteira_do_usuario(receita.carteira_id, usuario, sessao)
    sessao.delete(receita)
    sessao.commit()

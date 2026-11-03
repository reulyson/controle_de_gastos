"""CRUD de receitas."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoRecorrencia
from app.modulos.modelos import Receita
from app.nucleo.banco import obter_sessao
from app.nucleo_financeiro.servico_recorrencia import ServicoRecorrencia

roteador = APIRouter(prefix="/receitas", tags=["Receitas"])


class ReceitaCriar(BaseModel):
    """Criação de receita (contrato frontend)."""

    carteira_id: int | None = None
    descricao: str = Field(..., min_length=1, max_length=255)
    valor: Decimal = Field(..., max_digits=14, decimal_places=2)
    categoria_id: int | None = None
    recorrencia: TipoRecorrencia = TipoRecorrencia.UNICA
    mes_referencia: int | None = Field(default=None, ge=1, le=12)
    ano_referencia: int | None = Field(default=None, ge=2000)
    tag_ids: list[int] | None = None


class ReceitaAtualizar(BaseModel):
    """Atualização parcial."""

    descricao: str | None = None
    valor: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    categoria_id: int | None = None
    recorrencia: TipoRecorrencia | None = None
    ativo: bool | None = None


class ReceitaResposta(BaseModel):
    """Receita retornada."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    carteira_id: int | None = None
    descricao: str
    valor: Decimal
    categoria_id: int | None
    recorrencia: str
    tipo: str = "receita"
    mes_referencia: int | None = None
    ano_referencia: int | None = None
    ativo: bool


def _gerar_mensais_ao_criar(sessao: Session, receita: Receita, corpo: ReceitaCriar) -> None:
    if corpo.mes_referencia is None or corpo.ano_referencia is None:
        return
    meses = 12 if corpo.recorrencia == TipoRecorrencia.MENSAL else 1
    ServicoRecorrencia(sessao).gerar_receitas_mensais(
        receita.id,
        corpo.ano_referencia,
        corpo.mes_referencia,
        meses if meses > 1 else None,
    )


@roteador.get("", response_model=list[ReceitaResposta])
def listar(
    carteira_id: int | None = Query(default=None),
    sessao: Session = Depends(obter_sessao),
) -> list[ReceitaResposta]:
    """Lista receitas (filtro carteira reservado para multi-carteira)."""
    _ = carteira_id
    receitas = sessao.scalars(select(Receita)).all()
    return [
        ReceitaResposta(
            id=r.id,
            carteira_id=carteira_id,
            descricao=r.descricao,
            valor=r.valor,
            categoria_id=r.categoria_id,
            recorrencia=r.recorrencia,
            ativo=r.ativo,
        )
        for r in receitas
    ]


@roteador.post("", response_model=ReceitaResposta, status_code=201)
def criar(corpo: ReceitaCriar, sessao: Session = Depends(obter_sessao)) -> ReceitaResposta:
    """Cria receita e gera ocorrências mensais."""
    receita = Receita(
        descricao=corpo.descricao,
        valor=corpo.valor,
        categoria_id=corpo.categoria_id,
        recorrencia=corpo.recorrencia.value,
    )
    sessao.add(receita)
    sessao.commit()
    sessao.refresh(receita)
    _gerar_mensais_ao_criar(sessao, receita, corpo)
    return ReceitaResposta(
        id=receita.id,
        carteira_id=corpo.carteira_id,
        descricao=receita.descricao,
        valor=receita.valor,
        categoria_id=receita.categoria_id,
        recorrencia=receita.recorrencia,
        mes_referencia=corpo.mes_referencia,
        ano_referencia=corpo.ano_referencia,
        ativo=receita.ativo,
    )


@roteador.get("/{receita_id}", response_model=ReceitaResposta)
def obter(receita_id: int, sessao: Session = Depends(obter_sessao)) -> ReceitaResposta:
    """Obtém receita por ID."""
    receita = sessao.get(Receita, receita_id)
    if receita is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    return ReceitaResposta.model_validate(receita)


@roteador.put("/{receita_id}", response_model=ReceitaResposta)
@roteador.patch("/{receita_id}", response_model=ReceitaResposta)
def atualizar(
    receita_id: int,
    corpo: ReceitaAtualizar,
    sessao: Session = Depends(obter_sessao),
) -> ReceitaResposta:
    """Atualiza receita."""
    receita = sessao.get(Receita, receita_id)
    if receita is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    dados = corpo.model_dump(exclude_unset=True)
    if "recorrencia" in dados and dados["recorrencia"] is not None:
        dados["recorrencia"] = dados["recorrencia"].value
    for chave, valor in dados.items():
        setattr(receita, chave, valor)
    sessao.commit()
    sessao.refresh(receita)
    return ReceitaResposta.model_validate(receita)


@roteador.delete("/{receita_id}", status_code=204)
def excluir(receita_id: int, sessao: Session = Depends(obter_sessao)) -> None:
    """Exclui receita."""
    receita = sessao.get(Receita, receita_id)
    if receita is None:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    sessao.delete(receita)
    sessao.commit()

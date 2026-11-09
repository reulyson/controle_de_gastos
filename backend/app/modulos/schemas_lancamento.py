"""Schemas e helpers compartilhados de receita/despesa."""

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoRecorrencia
from app.modulos.modelos import Despesa, Receita
from app.nucleo_financeiro.servico_recorrencia import ServicoRecorrencia

TipoLancamentoStr = Literal["receita", "despesa"]


class LancamentoCriarBase(BaseModel):
    """Campos comuns ao criar receita ou despesa."""

    carteira_id: int
    descricao: str = Field(..., min_length=1, max_length=255)
    valor: Decimal = Field(..., max_digits=14, decimal_places=2)
    categoria_id: int | None = None
    recorrencia: TipoRecorrencia = TipoRecorrencia.UNICA
    mes_referencia: int | None = Field(default=None, ge=1, le=12)
    ano_referencia: int | None = Field(default=None, ge=2000)
    quantidade_meses: int | None = Field(default=None, ge=1, le=120)
    valor_variavel: bool = False


class LancamentoAtualizarBase(BaseModel):
    """Campos comuns ao atualizar receita ou despesa."""

    descricao: str | None = None
    valor: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    categoria_id: int | None = None
    recorrencia: TipoRecorrencia | None = None
    valor_variavel: bool | None = None
    ativo: bool | None = None


def quantidade_meses_efetiva(
    recorrencia: TipoRecorrencia,
    quantidade_meses: int | None,
) -> int | None:
    """Quantidade de competências a gerar; None = única ocorrência no serviço."""
    if recorrencia != TipoRecorrencia.MENSAL:
        return None
    return quantidade_meses if quantidade_meses is not None else 12


def gerar_mensais_ao_criar(
    sessao: Session,
    *,
    tipo: TipoLancamentoStr,
    lancamento_id: int,
    recorrencia: TipoRecorrencia,
    mes_referencia: int | None,
    ano_referencia: int | None,
    quantidade_meses: int | None,
) -> None:
    """Materializa linhas mensais após criar receita ou despesa."""
    if mes_referencia is None or ano_referencia is None:
        return
    meses = quantidade_meses_efetiva(recorrencia, quantidade_meses)
    servico = ServicoRecorrencia(sessao)
    if tipo == "receita":
        servico.gerar_receitas_mensais(lancamento_id, ano_referencia, mes_referencia, meses)
    elif tipo == "despesa":
        servico.gerar_despesas_mensais(lancamento_id, ano_referencia, mes_referencia, meses)
    else:
        raise ValueError(f"Tipo de lançamento inválido: {tipo}")


def aplicar_atualizacao_lancamento(
    *,
    entidade: Receita | Despesa,
    dados: dict[str, Any],
) -> None:
    """Aplica PATCH em receita/despesa."""
    if "recorrencia" in dados and dados["recorrencia"] is not None:
        valor_rec = dados["recorrencia"]
        dados["recorrencia"] = (
            valor_rec.value if isinstance(valor_rec, TipoRecorrencia) else valor_rec
        )
    for chave, valor in dados.items():
        setattr(entidade, chave, valor)

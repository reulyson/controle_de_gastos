"""Rotas REST de carteiras."""

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.modelos import Carteira, ContaFinanceira, Pagamento
from app.nucleo.banco import obter_sessao
from app.nucleo_financeiro.servico_calculos import ServicoCalculos
from app.nucleo_financeiro.servico_fechamento import ServicoFechamento
from app.nucleo_financeiro.servico_grade import ServicoGrade

roteador = APIRouter(prefix="/carteiras", tags=["Carteiras"])


class CarteiraResposta(BaseModel):
    """Representação de carteira alinhada ao frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    limite_cheque: Decimal
    saldo_inicial: Decimal
    ano_padrao: int | None = None

    @staticmethod
    def from_orm_carteira(carteira: Carteira, conta: ContaFinanceira | None) -> "CarteiraResposta":
        return CarteiraResposta(
            id=carteira.id,
            nome=carteira.nome,
            limite_cheque=carteira.limite_cheque_especial_total,
            saldo_inicial=conta.saldo_inicial if conta else Decimal("0.00"),
            ano_padrao=carteira.ano_padrao,
        )


class ConfiguracaoCarteiraCorpo(BaseModel):
    """Atualização de configuração da carteira."""

    limite_cheque: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    saldo_inicial: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    ano_padrao: int | None = Field(default=None, ge=2000, le=2100)


class FechamentoMesCorpo(BaseModel):
    """Corpo para fechar ou reabrir mês."""

    mes: int = Field(..., ge=1, le=12)
    ano: int = Field(..., ge=2000)


class AjusteExtratoCorpo(BaseModel):
    """Ajuste manual de extrato."""

    valor: Decimal = Field(..., max_digits=14, decimal_places=2)
    descricao: str | None = None
    data: date | None = None


class CelulaGradeResposta(BaseModel):
    """Célula da grade anual."""

    id: str
    linha_id: str
    mes: int
    valor: Decimal
    pago: bool
    tipo: str
    referencia_id: str | None = None


class LinhaGradeResposta(BaseModel):
    """Linha da grade."""

    id: str
    secao: str
    rotulo: str
    celulas: list[CelulaGradeResposta]
    total_anual: Decimal | None = None


class IndicadoresMesResposta(BaseModel):
    """KPIs do mês selecionado."""

    saldo_caixa: Decimal
    cheque_livre: Decimal
    receitas: Decimal
    despesas: Decimal
    orcado: Decimal
    pendencias: Decimal


class TotaisGradeResposta(BaseModel):
    """Totais consolidados."""

    total_receita: Decimal
    total_despesa: Decimal
    total_orcado: Decimal
    total_pago: Decimal
    caixa: Decimal


class MesStatusResposta(BaseModel):
    """Status de fechamento do mês."""

    mes: int
    status: str


class GradeControleResposta(BaseModel):
    """Grade anual completa."""

    ano: int
    mes_selecionado: int
    mes_fechado: bool | None = None
    indicadores: IndicadoresMesResposta
    linhas: list[LinhaGradeResposta] = Field(default_factory=list)
    totais: TotaisGradeResposta
    meses: list[MesStatusResposta] = Field(default_factory=list)
    pendencias_herdadas: list = Field(default_factory=list)


class RelatorioMesResposta(BaseModel):
    mes: int
    receitas: Decimal
    despesas: Decimal
    saldo: Decimal


class RelatorioCategoriaResposta(BaseModel):
    nome: str
    valor: Decimal
    tipo: str


class RelatorioResposta(BaseModel):
    meses: list[RelatorioMesResposta]
    por_categoria: list[RelatorioCategoriaResposta]


def _conta_da_carteira(sessao: Session, carteira_id: int) -> ContaFinanceira:
    conta = sessao.scalar(
        select(ContaFinanceira).where(ContaFinanceira.carteira_id == carteira_id)
    )
    if conta is None:
        raise HTTPException(status_code=404, detail="Conta da carteira não encontrada")
    return conta


@roteador.get("", response_model=list[CarteiraResposta])
def listar_carteiras(sessao: Session = Depends(obter_sessao)) -> list[CarteiraResposta]:
    """Lista carteiras cadastradas."""
    carteiras = sessao.scalars(select(Carteira)).all()
    resposta: list[CarteiraResposta] = []
    for carteira in carteiras:
        conta = sessao.scalar(
            select(ContaFinanceira).where(ContaFinanceira.carteira_id == carteira.id)
        )
        resposta.append(CarteiraResposta.from_orm_carteira(carteira, conta))
    return resposta


@roteador.patch("/{carteira_id}", response_model=CarteiraResposta)
def atualizar_carteira(
    carteira_id: int,
    corpo: ConfiguracaoCarteiraCorpo,
    sessao: Session = Depends(obter_sessao),
) -> CarteiraResposta:
    """Atualiza limite de cheque, saldo inicial e ano padrão."""
    carteira = sessao.get(Carteira, carteira_id)
    if carteira is None:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    conta = _conta_da_carteira(sessao, carteira_id)
    dados = corpo.model_dump(exclude_unset=True)
    if "limite_cheque" in dados and dados["limite_cheque"] is not None:
        carteira.limite_cheque_especial_total = dados["limite_cheque"]
    if "saldo_inicial" in dados and dados["saldo_inicial"] is not None:
        conta.saldo_inicial = dados["saldo_inicial"]
    if "ano_padrao" in dados:
        carteira.ano_padrao = dados["ano_padrao"]
    sessao.commit()
    sessao.refresh(carteira)
    sessao.refresh(conta)
    return CarteiraResposta.from_orm_carteira(carteira, conta)


@roteador.get("/{carteira_id}/anos/{ano}/grade-controle", response_model=GradeControleResposta)
def grade_controle(
    carteira_id: int,
    ano: int,
    mes: int | None = Query(default=None, ge=1, le=12),
    sessao: Session = Depends(obter_sessao),
) -> GradeControleResposta:
    """Retorna grade anual com indicadores do mês selecionado."""
    carteira = sessao.get(Carteira, carteira_id)
    if carteira is None:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    mes_sel = mes if mes is not None else 1
    dados = ServicoGrade(sessao).montar(carteira_id, ano, mes_sel)
    return GradeControleResposta.model_validate(dados)


@roteador.get("/{carteira_id}/anos/{ano}/relatorio", response_model=RelatorioResposta)
def relatorio_anual(
    carteira_id: int,
    ano: int,
    sessao: Session = Depends(obter_sessao),
) -> RelatorioResposta:
    """Relatório consolidado do ano."""
    if sessao.get(Carteira, carteira_id) is None:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    dados = ServicoCalculos(sessao).relatorio_anual(ano)
    return RelatorioResposta.model_validate(dados)


@roteador.post("/{carteira_id}/ajustes-extrato", status_code=204)
def ajustar_extrato(
    carteira_id: int,
    corpo: AjusteExtratoCorpo,
    sessao: Session = Depends(obter_sessao),
) -> None:
    """Registra ajuste de extrato na conta de caixa."""
    conta = _conta_da_carteira(sessao, carteira_id)
    dia = corpo.data or date.today()
    descricao = corpo.descricao or "Ajuste de extrato"
    pagamento = Pagamento(
        conta_id=conta.id,
        descricao=descricao,
        valor_total=corpo.valor,
        data_pagamento=dia,
    )
    sessao.add(pagamento)
    sessao.commit()


@roteador.post("/{carteira_id}/fechamentos", status_code=204)
def fechar_mes_carteira(
    carteira_id: int,
    corpo: FechamentoMesCorpo,
    sessao: Session = Depends(obter_sessao),
) -> None:
    """Fecha competência da carteira."""
    if sessao.get(Carteira, carteira_id) is None:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    try:
        ServicoFechamento(sessao).fechar_mes(corpo.ano, corpo.mes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@roteador.post("/{carteira_id}/fechamentos/reabrir", status_code=204)
def reabrir_mes_carteira(
    carteira_id: int,
    corpo: FechamentoMesCorpo,
    sessao: Session = Depends(obter_sessao),
) -> None:
    """Reabre competência fechada."""
    if sessao.get(Carteira, carteira_id) is None:
        raise HTTPException(status_code=404, detail="Carteira não encontrada")
    try:
        ServicoFechamento(sessao).reabrir_mes(corpo.ano, corpo.mes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

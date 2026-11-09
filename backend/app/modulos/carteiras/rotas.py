"""Rotas REST de carteiras."""

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.enumeracoes import TipoCarteira
from app.modulos.modelos import Carteira, ContaFinanceira, Usuario
from app.nucleo.banco import obter_sessao
from app.nucleo.deps_auth import obter_carteira_do_usuario, obter_usuario_atual
from app.nucleo_financeiro.servico_calculos import ServicoCalculos
from app.nucleo_financeiro.servico_fechamento import ServicoFechamento
from app.nucleo_financeiro.servico_grade import ServicoGrade

roteador = APIRouter(prefix="/carteiras", tags=["Carteiras"])


def _saldo_atual_carteira(sessao: Session, carteira_id: int) -> Decimal:
    """Saldo de caixa da competência atual (ano/mês de hoje)."""
    hoje = date.today()
    indicadores = ServicoCalculos(sessao, carteira_id).indicadores(hoje.year, hoje.month)
    return indicadores["saldo_caixa"]


class CarteiraResposta(BaseModel):
    """Representação de carteira alinhada ao frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    tipo_carteira: str = TipoCarteira.PESSOAL.value
    limite_cheque: Decimal
    saldo_inicial: Decimal
    saldo_atual: Decimal | None = None
    ano_padrao: int | None = None
    padrao: bool = False

    @staticmethod
    def from_orm_carteira(
        carteira: Carteira,
        conta: ContaFinanceira | None,
        *,
        sessao: Session | None = None,
    ) -> "CarteiraResposta":
        saldo_atual: Decimal | None = None
        if sessao is not None:
            saldo_atual = _saldo_atual_carteira(sessao, carteira.id)
        return CarteiraResposta(
            id=carteira.id,
            nome=carteira.nome,
            tipo_carteira=getattr(carteira, "tipo_carteira", None) or TipoCarteira.PESSOAL.value,
            limite_cheque=carteira.limite_cheque_especial_total,
            saldo_inicial=conta.saldo_inicial if conta else Decimal("0.00"),
            saldo_atual=saldo_atual,
            ano_padrao=carteira.ano_padrao,
            padrao=bool(carteira.padrao),
        )


class CarteiraCriarCorpo(BaseModel):
    """Criação de carteira do usuário."""

    nome: str = Field(..., min_length=1, max_length=120)
    tipo_carteira: TipoCarteira | None = None
    limite_cheque: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    saldo_inicial: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    ano_padrao: int | None = Field(default=None, ge=2000, le=2100)
    padrao: bool | None = None


class ConfiguracaoCarteiraCorpo(BaseModel):
    """Atualização de configuração da carteira."""

    nome: str | None = Field(default=None, min_length=1, max_length=120)
    tipo_carteira: TipoCarteira | None = None
    limite_cheque: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    saldo_inicial: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    ano_padrao: int | None = Field(default=None, ge=2000, le=2100)


class FechamentoMesCorpo(BaseModel):
    """Corpo para fechar ou reabrir mês."""

    mes: int = Field(..., ge=1, le=12)
    ano: int = Field(..., ge=2000)


class CelulaGradeResposta(BaseModel):
    id: str
    linha_id: str
    mes: int
    valor: Decimal
    pago: bool
    tipo: str
    referencia_id: str | None = None


class LinhaGradeResposta(BaseModel):
    id: str
    secao: str
    rotulo: str
    recorrencia: str | None = None
    celulas: list[CelulaGradeResposta]
    total_anual: Decimal | None = None


class IndicadoresMesResposta(BaseModel):
    saldo_caixa: Decimal
    cheque_livre: Decimal
    receitas: Decimal
    despesas: Decimal
    orcado: Decimal
    total_pago: Decimal = Decimal("0.00")
    pendencias: Decimal


class TotaisGradeResposta(BaseModel):
    total_receita: Decimal
    total_despesa: Decimal
    total_orcado: Decimal
    total_pago: Decimal
    caixa: Decimal


class MesStatusResposta(BaseModel):
    mes: int
    status: str


class GradeControleResposta(BaseModel):
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


def _definir_padrao_exclusiva(sessao: Session, usuario_id: int, carteira_id: int) -> None:
    outras = sessao.scalars(
        select(Carteira).where(
            Carteira.usuario_id == usuario_id,
            Carteira.id != carteira_id,
            Carteira.padrao.is_(True),
        )
    ).all()
    for outra in outras:
        outra.padrao = False
    alvo = sessao.get(Carteira, carteira_id)
    if alvo is not None:
        alvo.padrao = True


@roteador.get("", response_model=list[CarteiraResposta])
def listar_carteiras(
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> list[CarteiraResposta]:
    """Lista carteiras do usuário autenticado."""
    carteiras = sessao.scalars(
        select(Carteira).where(Carteira.usuario_id == usuario.id).order_by(Carteira.id)
    ).all()
    resposta: list[CarteiraResposta] = []
    for carteira in carteiras:
        conta = sessao.scalar(
            select(ContaFinanceira).where(ContaFinanceira.carteira_id == carteira.id)
        )
        resposta.append(CarteiraResposta.from_orm_carteira(carteira, conta, sessao=sessao))
    return resposta


@roteador.post("", response_model=CarteiraResposta, status_code=201)
def criar_carteira(
    corpo: CarteiraCriarCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> CarteiraResposta:
    """Cria carteira + conta; primeira vira padrão."""
    existentes = sessao.scalars(
        select(Carteira).where(Carteira.usuario_id == usuario.id)
    ).all()
    eh_primeira = len(existentes) == 0
    marcar_padrao = eh_primeira or bool(corpo.padrao)

    tipo = (corpo.tipo_carteira or TipoCarteira.PESSOAL).value
    carteira = Carteira(
        usuario_id=usuario.id,
        nome=corpo.nome.strip(),
        tipo_carteira=tipo,
        limite_cheque_especial_total=corpo.limite_cheque or Decimal("0.00"),
        ano_padrao=corpo.ano_padrao,
        padrao=marcar_padrao,
    )
    sessao.add(carteira)
    sessao.flush()
    if marcar_padrao and not eh_primeira:
        _definir_padrao_exclusiva(sessao, usuario.id, carteira.id)
    conta = ContaFinanceira(
        carteira_id=carteira.id,
        nome="Caixa",
        saldo_inicial=corpo.saldo_inicial or Decimal("0.00"),
    )
    sessao.add(conta)
    sessao.commit()
    sessao.refresh(carteira)
    sessao.refresh(conta)
    return CarteiraResposta.from_orm_carteira(carteira, conta, sessao=sessao)


@roteador.patch("/{carteira_id}/padrao", response_model=CarteiraResposta)
def definir_carteira_padrao(
    carteira_id: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> CarteiraResposta:
    """Define carteira padrão exclusiva do usuário."""
    carteira = obter_carteira_do_usuario(carteira_id, usuario, sessao)
    _definir_padrao_exclusiva(sessao, usuario.id, carteira.id)
    sessao.commit()
    sessao.refresh(carteira)
    conta = _conta_da_carteira(sessao, carteira.id)
    return CarteiraResposta.from_orm_carteira(carteira, conta, sessao=sessao)


@roteador.patch("/{carteira_id}", response_model=CarteiraResposta)
def atualizar_carteira(
    carteira_id: int,
    corpo: ConfiguracaoCarteiraCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> CarteiraResposta:
    """Atualiza limite de cheque, saldo inicial e ano padrão."""
    carteira = obter_carteira_do_usuario(carteira_id, usuario, sessao)
    conta = _conta_da_carteira(sessao, carteira_id)
    dados = corpo.model_dump(exclude_unset=True)
    if "nome" in dados and dados["nome"] is not None:
        carteira.nome = dados["nome"].strip()
    if "tipo_carteira" in dados and dados["tipo_carteira"] is not None:
        tipo = dados["tipo_carteira"]
        carteira.tipo_carteira = tipo.value if hasattr(tipo, "value") else str(tipo)
    if "limite_cheque" in dados and dados["limite_cheque"] is not None:
        carteira.limite_cheque_especial_total = dados["limite_cheque"]
    if "saldo_inicial" in dados and dados["saldo_inicial"] is not None:
        conta.saldo_inicial = dados["saldo_inicial"]
    if "ano_padrao" in dados:
        carteira.ano_padrao = dados["ano_padrao"]
    sessao.commit()
    sessao.refresh(carteira)
    sessao.refresh(conta)
    return CarteiraResposta.from_orm_carteira(carteira, conta, sessao=sessao)


class AnosCarteiraResposta(BaseModel):
    anos: list[int] = Field(default_factory=list)


@roteador.get("/{carteira_id}/anos", response_model=AnosCarteiraResposta)
def listar_anos_carteira(
    carteira_id: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> AnosCarteiraResposta:
    """Anos com dados (competências/faturas) na carteira."""
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    anos = ServicoGrade(sessao, carteira_id).listar_anos_com_dados(carteira_id)
    return AnosCarteiraResposta(anos=anos)


@roteador.get("/{carteira_id}/anos/{ano}/grade-controle", response_model=GradeControleResposta)
def grade_controle(
    carteira_id: int,
    ano: int,
    mes: int | None = Query(default=None, ge=1, le=12),
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> GradeControleResposta:
    """Retorna grade anual com indicadores do mês selecionado."""
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    mes_sel = mes if mes is not None else 1
    dados = ServicoGrade(sessao, carteira_id).montar(carteira_id, ano, mes_sel)
    return GradeControleResposta.model_validate(dados)


@roteador.get("/{carteira_id}/anos/{ano}/relatorio", response_model=RelatorioResposta)
def relatorio_anual(
    carteira_id: int,
    ano: int,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> RelatorioResposta:
    """Relatório consolidado do ano."""
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    dados = ServicoCalculos(sessao, carteira_id).relatorio_anual(ano)
    return RelatorioResposta.model_validate(dados)


@roteador.post("/{carteira_id}/fechamentos", status_code=204)
def fechar_mes_carteira(
    carteira_id: int,
    corpo: FechamentoMesCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> None:
    """Fecha competência da carteira."""
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    try:
        ServicoFechamento(sessao, carteira_id).fechar_mes(corpo.ano, corpo.mes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@roteador.post("/{carteira_id}/fechamentos/reabrir", status_code=204)
def reabrir_mes_carteira(
    carteira_id: int,
    corpo: FechamentoMesCorpo,
    sessao: Session = Depends(obter_sessao),
    usuario: Usuario = Depends(obter_usuario_atual),
) -> None:
    """Reabre competência fechada."""
    obter_carteira_do_usuario(carteira_id, usuario, sessao)
    try:
        ServicoFechamento(sessao, carteira_id).reabrir_mes(corpo.ano, corpo.mes)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

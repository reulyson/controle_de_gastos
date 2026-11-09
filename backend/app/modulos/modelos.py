"""Modelos SQLAlchemy 2 do FinFlow."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dominio.enumeracoes import (
    StatusFechamento,
    TipoCategoria,
    TipoCarteira,
    TipoCompraCartao,
    TipoRecorrencia,
)
from app.nucleo.banco import Base

MONETARIO = Numeric(14, 2)


class Usuario(Base):
    """Usuário autenticável do sistema."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    carteiras: Mapped[list["Carteira"]] = relationship(back_populates="usuario")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="usuario")


class RefreshToken(Base):
    """Refresh token opaco (armazenado como hash)."""

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revogado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="refresh_tokens")


class Carteira(Base):
    """Carteira financeira (agrupa conta e cartões)."""

    __tablename__ = "carteiras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo_carteira: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TipoCarteira.PESSOAL.value
    )
    limite_cheque_especial_total: Mapped[Decimal] = mapped_column(
        MONETARIO, nullable=False, default=Decimal("0.00")
    )
    ano_padrao: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    padrao: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="carteiras")
    conta: Mapped[Optional["ContaFinanceira"]] = relationship(back_populates="carteira", uselist=False)
    cartoes: Mapped[list["Cartao"]] = relationship(back_populates="carteira")


class ContaFinanceira(Base):
    """Conta de caixa única por carteira."""

    __tablename__ = "contas_financeiras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    carteira_id: Mapped[int] = mapped_column(ForeignKey("carteiras.id"), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, default="Caixa")
    saldo_inicial: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False, default=Decimal("0.00"))
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    carteira: Mapped["Carteira"] = relationship(back_populates="conta")
    pagamentos: Mapped[list["Pagamento"]] = relationship(back_populates="conta")


class Categoria(Base):
    """Categoria unificada: sistema (usuario_id NULL) ou pessoal do usuário."""

    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TipoCategoria.AMBOS.value
    )
    usuario_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True, index=True
    )

    __table_args__ = (
        UniqueConstraint("nome", "usuario_id", name="uq_categoria_nome_usuario"),
    )

    @property
    def origem(self) -> str:
        return "padrao" if self.usuario_id is None else "pessoal"


class Receita(Base):
    """Receita cadastrada (modelo ou recorrente)."""

    __tablename__ = "receitas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    carteira_id: Mapped[int] = mapped_column(ForeignKey("carteiras.id"), nullable=False, index=True)
    categoria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categorias.id"))
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    recorrencia: Mapped[str] = mapped_column(String(20), nullable=False, default=TipoRecorrencia.UNICA)
    valor_variavel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    mensais: Mapped[list["ReceitaMensal"]] = relationship(back_populates="receita")


class ReceitaMensal(Base):
    """Ocorrência mensal de receita."""

    __tablename__ = "receitas_mensais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receita_id: Mapped[int] = mapped_column(ForeignKey("receitas.id"), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    recebido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    receita: Mapped["Receita"] = relationship(back_populates="mensais")

    __table_args__ = (UniqueConstraint("receita_id", "ano", "mes", name="uq_receita_mensal"),)


class Despesa(Base):
    """Despesa cadastrada."""

    __tablename__ = "despesas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    carteira_id: Mapped[int] = mapped_column(ForeignKey("carteiras.id"), nullable=False, index=True)
    categoria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categorias.id"))
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    recorrencia: Mapped[str] = mapped_column(String(20), nullable=False, default=TipoRecorrencia.UNICA)
    valor_variavel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    mensais: Mapped[list["DespesaMensal"]] = relationship(back_populates="despesa")


class DespesaMensal(Base):
    """Ocorrência mensal de despesa."""

    __tablename__ = "despesas_mensais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    despesa_id: Mapped[int] = mapped_column(ForeignKey("despesas.id"), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    pago: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    despesa: Mapped["Despesa"] = relationship(back_populates="mensais")

    __table_args__ = (UniqueConstraint("despesa_id", "ano", "mes", name="uq_despesa_mensal"),)


class Pagamento(Base):
    """Pagamento registrado na conta de caixa."""

    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conta_id: Mapped[int] = mapped_column(ForeignKey("contas_financeiras.id"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    data_pagamento: Mapped[date] = mapped_column(Date, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    conta: Mapped["ContaFinanceira"] = relationship(back_populates="pagamentos")
    rateios: Mapped[list["PagamentoRateio"]] = relationship(back_populates="pagamento")


class PagamentoRateio(Base):
    """Rateio de pagamento entre categorias ou lançamentos."""

    __tablename__ = "pagamentos_rateios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pagamento_id: Mapped[int] = mapped_column(ForeignKey("pagamentos.id"), nullable=False)
    categoria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categorias.id"))
    despesa_mensal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("despesas_mensais.id"))
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(String(255))

    pagamento: Mapped["Pagamento"] = relationship(back_populates="rateios")


class Cartao(Base):
    """Cartão de crédito vinculado à carteira."""

    __tablename__ = "cartoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    carteira_id: Mapped[int] = mapped_column(ForeignKey("carteiras.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    bandeira: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    final_4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    limite: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False, default=Decimal("0.00"))
    dia_fechamento: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    dia_vencimento: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    carteira: Mapped["Carteira"] = relationship(back_populates="cartoes")
    compras: Mapped[list["CompraCartao"]] = relationship(back_populates="cartao")
    faturas: Mapped[list["Fatura"]] = relationship(back_populates="cartao")


class CompraCartao(Base):
    """Compra realizada no cartão."""

    __tablename__ = "compras_cartao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cartao_id: Mapped[int] = mapped_column(ForeignKey("cartoes.id"), nullable=False)
    categoria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categorias.id"))
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    tipo_compra: Mapped[str] = mapped_column(String(20), nullable=False, default=TipoCompraCartao.UNICA)
    data_compra: Mapped[date] = mapped_column(Date, nullable=False)
    parcelas_total: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    cartao: Mapped["Cartao"] = relationship(back_populates="compras")
    parcelas: Mapped[list["ParcelaCartao"]] = relationship(back_populates="compra")


class ParcelaCartao(Base):
    """Parcela de compra no cartão."""

    __tablename__ = "parcelas_cartao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    compra_id: Mapped[int] = mapped_column(ForeignKey("compras_cartao.id"), nullable=False)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)

    compra: Mapped["CompraCartao"] = relationship(back_populates="parcelas")


class Fatura(Base):
    """Fatura mensal de cartão."""

    __tablename__ = "faturas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cartao_id: Mapped[int] = mapped_column(ForeignKey("cartoes.id"), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False, default=Decimal("0.00"))
    paga: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cartao: Mapped["Cartao"] = relationship(back_populates="faturas")
    itens: Mapped[list["FaturaItem"]] = relationship(back_populates="fatura")
    pagamentos_fatura: Mapped[list["PagamentoFatura"]] = relationship(back_populates="fatura")

    __table_args__ = (UniqueConstraint("cartao_id", "ano", "mes", name="uq_fatura_cartao_mes"),)


class FaturaItem(Base):
    """Item lançado na fatura."""

    __tablename__ = "fatura_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fatura_id: Mapped[int] = mapped_column(ForeignKey("faturas.id"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    tipo_compra: Mapped[str] = mapped_column(String(20), nullable=False)
    parcela_id: Mapped[Optional[int]] = mapped_column(ForeignKey("parcelas_cartao.id"))
    marcado_pago: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    fatura: Mapped["Fatura"] = relationship(back_populates="itens")


class PagamentoFatura(Base):
    """Pagamento de fatura de cartão."""

    __tablename__ = "pagamentos_fatura"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fatura_id: Mapped[int] = mapped_column(ForeignKey("faturas.id"), nullable=False)
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    data_pagamento: Mapped[date] = mapped_column(Date, nullable=False)

    fatura: Mapped["Fatura"] = relationship(back_populates="pagamentos_fatura")


class FechamentoMensal(Base):
    """Fechamento contábil de um mês."""

    __tablename__ = "fechamentos_mensais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conta_id: Mapped[int] = mapped_column(ForeignKey("contas_financeiras.id"), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_inicial: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    saldo_final: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=StatusFechamento.ABERTO)

    pendencias: Mapped[list["FechamentoPendencia"]] = relationship(back_populates="fechamento")

    __table_args__ = (UniqueConstraint("conta_id", "ano", "mes", name="uq_fechamento_conta_mes"),)


class FechamentoPendencia(Base):
    """Pendência registrada no fechamento (sem duplicar linhas de lançamento)."""

    __tablename__ = "fechamento_pendencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fechamento_id: Mapped[int] = mapped_column(ForeignKey("fechamentos_mensais.id"), nullable=False)
    referencia_tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    referencia_id: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    valor: Mapped[Decimal] = mapped_column(MONETARIO, nullable=False)

    fechamento: Mapped["FechamentoMensal"] = relationship(back_populates="pendencias")


def garantir_bootstrap(sessao) -> None:
    """Garante dados iniciais do sistema (categorias padrão)."""
    from app.nucleo.seed_categorias import garantir_categorias_padrao

    garantir_categorias_padrao(sessao)

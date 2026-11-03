"""Registro de pagamentos com validação de cheque especial."""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.dominio.dinheiro import decimal_de
from app.dominio.liquidacao import SaldoInsuficienteError, validar_pagamento_com_cheque
from app.dominio.enumeracoes import TipoCompraCartao
from app.dominio.regras_cartao import regra_item_fatura
from app.modulos.modelos import DespesaMensal, FaturaItem, Pagamento, PagamentoRateio, ReceitaMensal
from app.nucleo_financeiro.servico_calculos import ServicoCalculos


class ServicoPagamentos:
    """Marca despesas como pagas e registra pagamentos."""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao
        self._calculos = ServicoCalculos(sessao)

    def saldo_atual(self) -> Decimal:
        """Estima saldo de caixa com base nos totais do mês corrente.

        Returns:
            Decimal: Saldo atual aproximado.
        """
        hoje = date.today()
        totais = self._calculos.totais_competencia(hoje.year, hoje.month)
        return totais.saldo_caixa

    def registrar_pagamento(
        self,
        descricao: str,
        valor: Decimal,
        data_pagamento: date,
        despesa_mensal_id: int | None = None,
        categoria_id: int | None = None,
    ) -> Pagamento:
        """Registra pagamento após validar limite de cheque.

        Args:
            descricao: Texto do pagamento.
            valor: Valor debitado.
            data_pagamento: Data efetiva.
            despesa_mensal_id: Despesa mensal associada (opcional).
            categoria_id: Categoria do rateio (opcional).

        Returns:
            Pagamento: Registro persistido.

        Raises:
            SaldoInsuficienteError: Se ultrapassar cheque especial.
        """
        conta = self._calculos.obter_conta_unica()
        carteira = self._calculos.obter_carteira()
        valor_q = decimal_de(valor)
        validar_pagamento_com_cheque(
            self.saldo_atual(),
            valor_q,
            carteira.limite_cheque_especial_total,
        )

        pagamento = Pagamento(
            conta_id=conta.id,
            descricao=descricao,
            valor_total=valor_q,
            data_pagamento=data_pagamento,
        )
        self._sessao.add(pagamento)
        self._sessao.flush()

        rateio = PagamentoRateio(
            pagamento_id=pagamento.id,
            valor=valor_q,
            categoria_id=categoria_id,
            despesa_mensal_id=despesa_mensal_id,
            descricao=descricao,
        )
        self._sessao.add(rateio)

        if despesa_mensal_id is not None:
            despesa_mensal = self._sessao.get(DespesaMensal, despesa_mensal_id)
            if despesa_mensal is not None:
                despesa_mensal.pago = True

        self._sessao.commit()
        self._sessao.refresh(pagamento)
        return pagamento

    def marcar_despesa_paga(self, despesa_mensal_id: int, data_pagamento: date | None = None) -> Pagamento:
        """Marca despesa mensal como paga criando pagamento.

        Args:
            despesa_mensal_id: ID da linha mensal.
            data_pagamento: Data do pagamento (hoje se omitida).

        Returns:
            Pagamento: Pagamento criado.

        Raises:
            SaldoInsuficienteError: Se saldo insuficiente.
            ValueError: Se despesa não existir.
        """
        despesa_mensal = self._sessao.get(DespesaMensal, despesa_mensal_id)
        if despesa_mensal is None:
            msg = "Despesa mensal não encontrada"
            raise ValueError(msg)
        dia = data_pagamento or date.today()
        return self.registrar_pagamento(
            descricao=f"Pagamento despesa #{despesa_mensal_id}",
            valor=despesa_mensal.valor,
            data_pagamento=dia,
            despesa_mensal_id=despesa_mensal_id,
        )

    def alternar(
        self,
        tipo: str,
        referencia_id: int,
        ano: int,
        mes: int,
        pago: bool,
    ) -> None:
        """Alterna status pago/recebido conforme tipo de lançamento.

        Args:
            tipo: receita, despesa ou cartao.
            referencia_id: ID da linha mensal ou item de fatura.
            ano: Competência informada pelo cliente.
            mes: Competência informada pelo cliente.
            pago: Novo estado desejado.

        Raises:
            SaldoInsuficienteError: Cheque insuficiente ao pagar despesa.
            ValueError: Referência inválida ou operação não permitida.
        """
        _ = (ano, mes)
        if tipo == "receita":
            linha = self._sessao.get(ReceitaMensal, referencia_id)
            if linha is None:
                msg = "Receita mensal não encontrada"
                raise ValueError(msg)
            linha.recebido = pago
            self._sessao.commit()
            return
        if tipo == "despesa":
            linha = self._sessao.get(DespesaMensal, referencia_id)
            if linha is None:
                msg = "Despesa mensal não encontrada"
                raise ValueError(msg)
            if pago:
                if not linha.pago:
                    self.marcar_despesa_paga(referencia_id)
                return
            linha.pago = False
            self._sessao.commit()
            return
        if tipo == "cartao":
            item = self._sessao.get(FaturaItem, referencia_id)
            if item is None:
                msg = "Item de fatura não encontrado"
                raise ValueError(msg)
            regra = regra_item_fatura(TipoCompraCartao(item.tipo_compra))
            if not regra.permite_marcar_pago:
                msg = "Item não permite marcar pagamento"
                raise ValueError(msg)
            item.marcado_pago = pago
            self._sessao.commit()
            return
        msg = f"Tipo de pagamento inválido: {tipo}"
        raise ValueError(msg)

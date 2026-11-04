# ETAPA 02 - VENDA ATOMICA, DESCONTOS POR PRODUTO E HISTORICO
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import sqlite3
from banco import conectar, criar_banco, consultar_produtos
from interface import titulo

CENTAVO = Decimal('0.01')
FUSO = timezone(timedelta(hours=-3))


def centavos(valor):
    return int((valor.quantize(CENTAVO, rounding=ROUND_HALF_UP) * 100))


def dinheiro_centavos(valor):
    return f'R$ {valor / 100:.2f}'


def ler_quantidade(disponivel):
    while True:
        entrada = input('Digite a quantidade (Enter=pular, V=voltar): ').strip().upper()
        if entrada == 'V':
            return None
        if not entrada:
            return 0
        try:
            qtd = int(entrada)
        except ValueError:
            print('Digite quantidade inteira ou V.')
            continue
        if 0 <= qtd <= disponivel:
            return qtd
        print('Quantidade fora do estoque!')


def ler_desconto():
    while True:
        entrada = input('Desconto % (Enter=nenhum, V=voltar): ').strip().upper()
        if entrada == 'V':
            return None
        if not entrada:
            return Decimal('0')
        try:
            valor = Decimal(entrada)
        except InvalidOperation:
            print('Percentual invalido.')
            continue
        if valor.is_finite() and (valor == 0 or Decimal(1) <= valor <= Decimal(3)):
            return valor
        print('Permitido: 0 ou percentual de 1% a 3%.')


def registrar_pedido():
    criar_banco()
    titulo('NOVO PEDIDO - SQLITE')
    pedido = []
    for identificador, nome, preco, estoque in consultar_produtos():
        print(f'\nPRODUTO: {nome}\nPRECO: R$ {preco:.2f}\nESTOQUE: {estoque}')
        qtd = ler_quantidade(estoque)
        if qtd is None:
            print('Pedido cancelado.'); return
        if not qtd:
            continue
        desconto = ler_desconto()
        if desconto is None:
            print('Pedido cancelado.'); return
        unitario = centavos(Decimal(str(preco)))
        bruto = unitario * qtd
        abatimento = centavos(Decimal(bruto) / 100 * desconto / 100)
        liquido = bruto - abatimento
        pedido.append((identificador, nome, qtd, unitario, desconto,
                       bruto, abatimento, liquido))
    if not pedido:
        print('Pedido vazio.'); return
    subtotal = sum(item[5] for item in pedido)
    descontos = sum(item[6] for item in pedido)
    total = subtotal - descontos
    titulo('RESUMO DO PEDIDO')
    for item in pedido:
        print(f'{item[1]:<12} qtd:{item[2]:>3} desc:{item[4]}% total: {dinheiro_centavos(item[7])}')
    print('Subtotal:', dinheiro_centavos(subtotal))
    print('Descontos:', dinheiro_centavos(descontos))
    print('TOTAL:', dinheiro_centavos(total))
    while True:
        resposta = input('Confirmar venda (S/N/V)? ').strip().upper()
        if resposta in ('S','N','V'):
            break
        print('Digite S, N ou V.')
    if resposta != 'S':
        print('Venda cancelada.'); return

    # Uma transacao: tudo confirma ou tudo e revertido.
    db = conectar()
    try:
        db.execute('BEGIN IMMEDIATE')
        # Validar e descontar cada produto na mesma transacao.
        for item in pedido:
            atualizacao = db.execute('''UPDATE produtos SET quantidade = quantidade - ?
                    WHERE id = ? AND quantidade >= ?''', (item[2], item[0], item[2]))
            if atualizacao.rowcount != 1:
                raise ValueError(f'Estoque insuficiente ou produto ausente: {item[1]}')
        cursor = db.execute('''INSERT INTO vendas
            (data_hora,subtotal_centavos,descontos_centavos,total_centavos)
            VALUES (?,?,?,?)''', (datetime.now(FUSO).isoformat(timespec='seconds'),
                                   subtotal, descontos, total))
        venda_id = cursor.lastrowid
        db.executemany('''INSERT INTO itens_venda
            (venda_id,produto_id,nome_produto,quantidade,preco_unitario_centavos,
             desconto_percentual,valor_desconto_centavos,total_centavos)
            VALUES (?,?,?,?,?,?,?,?)''',
            [(venda_id, i[0], i[1], i[2], i[3], str(i[4]), i[6], i[7]) for i in pedido])
        db.commit()
    except (sqlite3.Error, ValueError) as erro:
        db.rollback()
        print('VENDA NAO REGISTRADA:', erro)
        return
    finally:
        db.close()
    print(f'Venda {venda_id} confirmada e salva no banco!')

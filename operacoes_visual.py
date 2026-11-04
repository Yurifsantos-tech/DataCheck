"""Operacoes da interface DataCheck Aula 49. Reusa o banco existente."""
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from sqlite3 import IntegrityError
from banco import conectar, consultar_produtos
from cadastro_db import preparar_cadastros
from recebimento_db import cadastrar_nota, adicionar_item, receber_nota, listar_notas, listar_itens, preparar_recebimentos, FUSO


def cadastrar_fornecedor(codigo, nome, cidade, estado, cep, telefone, endereco):
    campos = (codigo, nome, cidade, estado, cep, telefone, endereco)
    if not all(str(x).strip() for x in campos):
        raise ValueError('Preencha todos os campos do fornecedor.')
    preparar_cadastros()
    with conectar() as db:
        db.execute('''INSERT INTO fornecedores(codigo,nome,cidade,estado,cep,telefone,endereco)
                      VALUES(?,?,?,?,?,?,?)''', tuple(str(x).strip() for x in campos))


def registrar_venda(itens):
    """itens: lista (produto_id, quantidade, desconto_percentual). Transacao unica."""
    if not itens:
        raise ValueError('Escolha ao menos um produto para a venda.')
    ids = [int(item[0]) for item in itens]
    if len(ids) != len(set(ids)):
        raise ValueError('Produto repetido no pedido.')
    db = conectar()
    try:
        db.execute('BEGIN IMMEDIATE')
        linhas = []
        for produto_id, quantidade, desconto_texto in itens:
            if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
                raise ValueError('Quantidade deve ser um numero inteiro positivo.')
            try:
                desconto = Decimal(str(desconto_texto).replace(',', '.'))
            except InvalidOperation as erro:
                raise ValueError('Desconto invalido.') from erro
            if not desconto.is_finite() or not (desconto == 0 or Decimal('1') <= desconto <= Decimal('3')):
                raise ValueError('Desconto permitido: zero ou de 1% a 3%.')
            produto = db.execute('SELECT nome,preco_venda,quantidade FROM produtos WHERE id=?', (produto_id,)).fetchone()
            if not produto:
                raise ValueError('Produto nao encontrado.')
            nome, preco, disponivel = produto
            if quantidade > disponivel:
                raise ValueError(f'Estoque insuficiente para {nome}. Disponivel: {disponivel}.')
            preco_centavos = int((Decimal(str(preco))*100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            bruto = preco_centavos * quantidade
            abatimento = int((Decimal(bruto)*desconto/Decimal(100)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            linhas.append((produto_id,nome,quantidade,preco_centavos,str(desconto),bruto,abatimento,bruto-abatimento))
        subtotal = sum(x[5] for x in linhas)
        descontos = sum(x[6] for x in linhas)
        total = subtotal - descontos
        for item in linhas:
            cur = db.execute('UPDATE produtos SET quantidade=quantidade-? WHERE id=? AND quantidade>=?', (item[2],item[0],item[2]))
            if cur.rowcount != 1:
                raise ValueError('Estoque alterado durante a venda. Operacao cancelada.')
        cursor = db.execute('INSERT INTO vendas(data_hora,subtotal_centavos,descontos_centavos,total_centavos) VALUES(?,?,?,?)',
                            (datetime.now(FUSO).isoformat(timespec='seconds'),subtotal,descontos,total))
        venda_id = cursor.lastrowid
        db.executemany('''INSERT INTO itens_venda(venda_id,produto_id,nome_produto,quantidade,
                         preco_unitario_centavos,desconto_percentual,valor_desconto_centavos,total_centavos)
                         VALUES(?,?,?,?,?,?,?,?)''', [(venda_id,x[0],x[1],x[2],x[3],x[4],x[6],x[7]) for x in linhas])
        db.commit()
        return venda_id, total
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

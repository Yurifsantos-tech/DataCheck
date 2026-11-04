"""Aula 44 — relatório de entradas e vendas, somente leitura."""
from decimal import Decimal
from banco import conectar


def reais(centavos):
    valor = Decimal(centavos) / 100
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def mostrar_movimentacoes():
    with conectar() as db:
        print('\n=== ENTRADAS DE MERCADORIAS (NOTAS RECEBIDAS) ===')
        recebimentos = db.execute('''
            SELECT r.id, r.data_hora, n.numero, n.serie, f.nome, r.total_centavos
            FROM recebimentos r JOIN notas_fiscais n ON n.id=r.nota_id
            JOIN fornecedores f ON f.codigo=n.fornecedor_codigo ORDER BY r.id
        ''').fetchall()
        if not recebimentos:
            print('Nenhum recebimento confirmado.')
        for rid, data, nf, serie, fornecedor, total in recebimentos:
            print(f'\nRecebimento {rid} | {data} | NF {nf}/{serie} | {fornecedor} | {reais(total)}')
            itens = db.execute('''SELECT p.nome, m.quantidade, m.custo_unitario_centavos
                 FROM movimentos_estoque m JOIN produtos p ON p.id=m.produto_id
                 WHERE m.recebimento_id=? ORDER BY m.id''', (rid,)).fetchall()
            for nome, qtd, custo in itens:
                print(f'  + {qtd} x {nome} | custo un. {reais(custo)} | total {reais(qtd*custo)}')
        print('\n=== SAIDAS POR VENDAS ===')
        vendas = db.execute('''SELECT id, data_hora, total_centavos FROM vendas ORDER BY id''').fetchall()
        if not vendas:
            print('Nenhuma venda registrada.')
        for vid, data, total in vendas:
            print(f'\nVenda {vid} | {data} | total {reais(total)}')
            itens = db.execute('''SELECT nome_produto, quantidade, total_centavos
                FROM itens_venda WHERE venda_id=? ORDER BY id''', (vid,)).fetchall()
            for nome, qtd, subtotal in itens:
                print(f'  - {qtd} x {nome} | total liquido {reais(subtotal)}')
        print('\n=== SALDO ATUAL DE PRODUTOS ===')
        for nome, quantidade in db.execute('SELECT nome, quantidade FROM produtos ORDER BY id'):
            print(f'{nome:<16} {quantidade:>7} un.')
        print('\nObservacao: movimentos de vendas sao apresentados a partir de itens_venda;'
              ' nao constituem um razao historico completo de todas as alteracoes do estoque.')


if __name__ == '__main__':
    try:
        mostrar_movimentacoes()
    except Exception as erro:
        print(f'Falha na consulta: {erro}')

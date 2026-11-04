# ETAPA 03 - RELATORIO DE VENDAS PERSISTENTES
from banco import conectar, criar_banco
from interface import titulo
from vendas import dinheiro_centavos


def relatorio():
    criar_banco()
    titulo('HISTORICO DE VENDAS - SQLITE')
    with conectar() as db:
        vendas = db.execute('''SELECT id,data_hora,subtotal_centavos,
            descontos_centavos,total_centavos FROM vendas ORDER BY id''').fetchall()
        itens = db.execute('''SELECT venda_id,nome_produto,quantidade,
            desconto_percentual,total_centavos FROM itens_venda ORDER BY id''').fetchall()
    if not vendas:
        print('Nenhuma venda registrada.')
    else:
        for identificador, data, bruto, desc, total in vendas:
            print(f'\nPedido #{identificador} | {data}')
            for venda_id, nome, qtd, percentual, total_item in itens:
                if venda_id == identificador:
                    print(f'  {nome}: {qtd} un. | {percentual}% | {dinheiro_centavos(total_item)}')
            print('Total:', dinheiro_centavos(total))
        print('\nPedidos realizados:', len(vendas))
        print('Total vendido:', dinheiro_centavos(sum(v[4] for v in vendas)))
        print('Descontos concedidos:', dinheiro_centavos(sum(v[3] for v in vendas)))
    input('\nPressione Enter para voltar ao menu.')

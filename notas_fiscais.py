"""DataCheck - notas fiscais SQLite, inclusão de vários itens em uma operação."""
from datetime import datetime
from sqlite3 import IntegrityError
from banco import conectar, consultar_produtos
from interface import titulo
from recebimento_db import (
    FUSO, preparar_recebimentos, cadastrar_nota, adicionar_item,
    receber_nota, listar_notas, listar_itens,
)


def _reais(centavos):
    s = f'{centavos / 100:,.2f}'
    return 'R$ ' + s.replace(',', '#').replace('.', ',').replace('#', '.')


def _inteiro_positivo(msg):
    while True:
        texto = input(msg).strip()
        if texto.upper() == 'V':
            return None
        if texto.isdigit() and int(texto) > 0:
            return int(texto)
        print('Informe um numero inteiro positivo ou V para voltar.')


def _mostrar_notas():
    notas = listar_notas()
    if not notas:
        print('Nenhuma nota no banco SQLite.')
    for id_, numero, serie, emissao, fornecedor, status in notas:
        print(f'\nID INTERNO {id_} | NF {numero}/{serie} | {emissao} | {fornecedor} | {status}')
        itens = listar_itens(id_)
        total = 0
        unidades = 0
        if not itens:
            print('  Nenhum item cadastrado nesta nota.')
        else:
            print(f"  {'PRODUTO':<15} {'QTD':>5} {'CUSTO UN.':>14} {'SUBTOTAL':>15}")
            print('  ' + '-' * 53)
        for nome, qtd, custo_centavos in itens:
            subtotal = qtd * custo_centavos
            total += subtotal
            unidades += qtd
            print(f'  {nome:<15} {qtd:>5} {_reais(custo_centavos):>14} {_reais(subtotal):>15}')
        print(f'  TOTAL DE UNIDADES: {unidades}')
        print(f'  TOTAL DA NOTA: {_reais(total)}')
    return notas


def _criar():
    with conectar() as db:
        fornecedores = db.execute('SELECT codigo, nome FROM fornecedores ORDER BY nome').fetchall()
    if not fornecedores:
        print('Cadastre um fornecedor no SQLite antes de criar uma NF.')
        return
    numero = input('Numero da NF (V=voltar): ').strip()
    if numero.upper() == 'V':
        return
    if not numero.isdigit() or int(numero) <= 0:
        print('Numero invalido.')
        return
    serie = input('Serie da NF (V=voltar): ').strip()
    if serie.upper() == 'V':
        return
    if not serie.isdigit():
        print('Serie deve ser numerica.')
        return
    emissao = input('Emissao DD/MM/AAAA (V=voltar): ').strip()
    if emissao.upper() == 'V':
        return
    try:
        data = datetime.strptime(emissao, '%d/%m/%Y').date()
        if data > datetime.now(FUSO).date():
            print('Data futura nao permitida.')
            return
    except ValueError:
        print('Data invalida.')
        return
    print('Fornecedores:')
    for codigo, nome in fornecedores:
        print(f'  {codigo} - {nome}')
    codigo = input('Codigo do fornecedor (V=voltar): ').strip()
    if codigo.upper() == 'V':
        return
    if codigo not in {item[0] for item in fornecedores}:
        print('Fornecedor nao encontrado no SQLite.')
        return
    try:
        id_ = cadastrar_nota(numero, serie, emissao, codigo)
        print(f'Rascunho criado. ID interno da nota: {id_}')
    except IntegrityError:
        print('NF duplicada ou fornecedor inexistente. Nenhum cadastro realizado.')


def _selecionar_nota():
    notas = _mostrar_notas()
    disponiveis = {id_ for id_, _, _, _, _, status in notas if status == 'RASCUNHO'}
    if not disponiveis:
        print('Nenhuma nota em rascunho para selecionar.')
        return None
    while True:
        nota_id = _inteiro_positivo('ID INTERNO da NF (V=voltar): ')
        if nota_id is None:
            return None
        if nota_id in disponiveis:
            return nota_id
        print('ID invalido ou nota ja recebida. Use o ID INTERNO mostrado na lista, nao o numero da NF.')


def _adicionar():
    nota_id = _selecionar_nota()
    if nota_id is None:
        return
    print('\nAdicione quantos produtos quiser nesta mesma nota. Digite V no ID do produto para encerrar.')
    while True:
        produtos = {id_: (nome, preco, qtd) for id_, nome, preco, qtd in consultar_produtos()}
        print('\nPRODUTOS CADASTRADOS')
        for id_, (nome, preco, qtd) in produtos.items():
            print(f'{id_} - {nome} | Estoque {qtd} | Preco VENDA {_reais(round(preco * 100))}')
        produto_id = _inteiro_positivo('ID do PRODUTO (V=finalizar inclusao): ')
        if produto_id is None:
            break
        if produto_id not in produtos:
            print('Produto inexistente. Escolha um ID exibido acima.')
            continue
        nome = produtos[produto_id][0]
        qtd = _inteiro_positivo(f'Quantidade recebida de {nome} (V=cancelar item): ')
        if qtd is None:
            continue
        custo = input(f'Custo unitario de COMPRA de {nome} (ex. 10,00; V=cancelar item): ').strip()
        if custo.upper() == 'V':
            continue
        try:
            adicionar_item(nota_id, produto_id, qtd, custo)
            print(f'{nome}: {qtd} unidade(s) registradas na nota. Estoque ainda nao alterado.')
        except (ValueError, IntegrityError) as erro:
            print('Item NAO cadastrado:', erro)
        print('\nTOTAL ATUALIZADO DA NOTA:')
        itens = listar_itens(nota_id)
        total = sum(quantidade * cents for _, quantidade, cents in itens)
        print(_reais(total))
    print('\nInclusao encerrada. Confira a opcao [2] antes de receber a nota.')


def _receber():
    nota_id = _selecionar_nota()
    if nota_id is None:
        return
    itens = listar_itens(nota_id)
    if not itens:
        print('Nota sem itens: recebimento nao permitido.')
        return
    print('\nITENS QUE SERAO ADICIONADOS AO ESTOQUE:')
    total = 0
    for nome, qtd, cents in itens:
        parcial = qtd * cents
        total += parcial
        print(f'{nome}: +{qtd} un. x {_reais(cents)} = {_reais(parcial)}')
    print(f'TOTAL: {_reais(total)}')
    if input('Confirmar recebimento DEFINITIVO? Digite SIM: ').strip().upper() != 'SIM':
        print('Operacao cancelada. Estoque preservado.')
        return
    try:
        total_recebido = receber_nota(nota_id)
        print(f'Recebimento concluido. Total de custo: {_reais(total_recebido)}')
        print('Estoque atualizado e movimentacao gravada.')
    except (ValueError, IntegrityError) as erro:
        print('Recebimento NAO realizado:', erro)


def modulo_entradas():
    preparar_recebimentos()
    while True:
        titulo('ENTRADA DE MERCADORIAS - SQLITE')
        print('[1] Cadastrar nota fiscal (rascunho)')
        print('[2] Consultar notas fiscais e itens')
        print('[3] Adicionar VARIOS itens a uma nota')
        print('[4] Confirmar recebimento e atualizar estoque')
        print('[V] Voltar ao menu')
        opcao = input('Escolha: ').strip().upper()
        if opcao == 'V':
            return
        elif opcao == '1':
            _criar()
        elif opcao == '2':
            _mostrar_notas()
            input('Pressione Enter para continuar.')
        elif opcao == '3':
            _adicionar()
        elif opcao == '4':
            _receber()
        else:
            print('Opcao invalida.')

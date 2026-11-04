"""Aula 45 — auditoria de integridade, somente leitura."""
from banco import conectar


def auditar():
    problemas = []
    with conectar() as db:
        resultado = db.execute('PRAGMA integrity_check').fetchone()[0]
        if resultado != 'ok':
            problemas.append(f'Integridade do SQLite: {resultado}')
        fks = db.execute('PRAGMA foreign_key_check').fetchall()
        if fks:
            problemas.append(f'{len(fks)} referencia(s) de chave estrangeira inconsistente(s).')
        negativos = db.execute('SELECT nome, quantidade FROM produtos WHERE quantidade < 0').fetchall()
        if negativos:
            problemas.append(f'Produtos com estoque negativo: {negativos}')
        recebimentos = db.execute('''SELECT r.id, r.nota_id, r.total_centavos,
            COALESCE((SELECT SUM(i.quantidade*i.custo_unitario_centavos)
                      FROM itens_nota i WHERE i.nota_id=r.nota_id),0),
            COALESCE((SELECT SUM(m.quantidade*m.custo_unitario_centavos)
                      FROM movimentos_estoque m WHERE m.recebimento_id=r.id),0)
            FROM recebimentos r''').fetchall()
        for rid, nid, registrado, itens, movimentos in recebimentos:
            if registrado != itens:
                problemas.append(f'Recebimento {rid}/NF-ID {nid}: total difere dos itens.')
            if registrado != movimentos:
                problemas.append(f'Recebimento {rid}/NF-ID {nid}: total difere dos movimentos.')
            itens_produto = db.execute('''SELECT produto_id,SUM(quantidade) FROM itens_nota
                WHERE nota_id=? GROUP BY produto_id''', (nid,)).fetchall()
            movimentos_produto = db.execute('''SELECT produto_id,SUM(quantidade) FROM movimentos_estoque
                WHERE recebimento_id=? GROUP BY produto_id''', (rid,)).fetchall()
            if dict(itens_produto) != dict(movimentos_produto):
                problemas.append(f'Recebimento {rid}: produtos/quantidades diferem dos itens da nota.')
        vendas = db.execute('''SELECT v.id, v.total_centavos,
            COALESCE((SELECT SUM(i.total_centavos) FROM itens_venda i WHERE i.venda_id=v.id),0)
            FROM vendas v''').fetchall()
        for vid, registrado, itens in vendas:
            if registrado != itens:
                problemas.append(f'Venda {vid}: total registrado diferente da soma dos itens.')
        nprodutos = db.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]
        nfornecedores = db.execute('SELECT COUNT(*) FROM fornecedores').fetchone()[0]
        nnotas = db.execute('SELECT COUNT(*) FROM notas_fiscais').fetchone()[0]
        print('\n=== AUDITORIA DATACHECK (SOMENTE LEITURA) ===')
        print(f'Produtos: {nprodutos} | Fornecedores: {nfornecedores} | Notas: {nnotas}')
        print(f'Vendas: {len(vendas)} | Recebimentos: {len(recebimentos)}')
        if problemas:
            print(f'ATENCAO: {len(problemas)} inconsistencia(s) encontrada(s):')
            for problema in problemas:
                print(' -', problema)
        else:
            print('Nenhuma inconsistencia detectada pelas verificacoes implementadas.')
        print('Limite: a auditoria nao comprova saldo historico completo sem estoque inicial e')
        print('registro de toda movimentacao; nao substitui conciliacao fisica.')
    return problemas


if __name__ == '__main__':
    try:
        auditar()
    except Exception as erro:
        print(f'Nao foi possivel auditar: {erro}')

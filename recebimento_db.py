"""Aulas 42/43: itens de nota e recebimento atomico de mercadorias."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from banco import conectar
from cadastro_db import preparar_cadastros

FUSO = timezone(timedelta(hours=-3))


def centavos(valor):
    try:
        numero = Decimal(str(valor).replace(',', '.'))
        if not numero.is_finite() or numero < 0:
            raise ValueError('Custo invalido.')
        return int((numero * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError('Informe um custo monetario valido.') from exc


def preparar_recebimentos():
    preparar_cadastros()
    with conectar() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS itens_nota (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota_id INTEGER NOT NULL REFERENCES notas_fiscais(id),
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            custo_unitario_centavos INTEGER NOT NULL CHECK(custo_unitario_centavos >= 0)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS recebimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota_id INTEGER NOT NULL UNIQUE REFERENCES notas_fiscais(id),
            data_hora TEXT NOT NULL,
            total_centavos INTEGER NOT NULL CHECK(total_centavos >= 0)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS movimentos_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recebimento_id INTEGER NOT NULL REFERENCES recebimentos(id),
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            quantidade INTEGER NOT NULL CHECK(quantidade > 0),
            custo_unitario_centavos INTEGER NOT NULL CHECK(custo_unitario_centavos >= 0)
        )''')


def cadastrar_nota(numero, serie, emissao, fornecedor_codigo):
    preparar_recebimentos()
    with conectar() as db:
        cursor = db.execute('''INSERT INTO notas_fiscais
            (numero, serie, emissao, fornecedor_codigo, situacao)
            VALUES (?, ?, ?, ?, 'RASCUNHO')''',
            (numero, serie, emissao, fornecedor_codigo))
        return cursor.lastrowid


def adicionar_item(nota_id, produto_id, quantidade, custo):
    if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
        raise ValueError('Quantidade deve ser um inteiro positivo.')
    custo_cents = centavos(custo)
    with conectar() as db:
        if db.execute('SELECT 1 FROM recebimentos WHERE nota_id=?', (nota_id,)).fetchone():
            raise ValueError('Esta nota ja foi recebida.')
        if not db.execute('SELECT 1 FROM notas_fiscais WHERE id=?', (nota_id,)).fetchone():
            raise ValueError('Nota fiscal inexistente.')
        if not db.execute('SELECT 1 FROM produtos WHERE id=?', (produto_id,)).fetchone():
            raise ValueError('Produto inexistente.')
        db.execute('''INSERT INTO itens_nota (nota_id, produto_id, quantidade, custo_unitario_centavos)
            VALUES (?, ?, ?, ?)''', (nota_id, produto_id, quantidade, custo_cents))


def receber_nota(nota_id):
    """Transacao unica: recebimento, movimentacoes e alteracao do estoque."""
    with conectar() as db:
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT 1 FROM notas_fiscais WHERE id=?', (nota_id,)).fetchone():
            raise ValueError('Nota fiscal inexistente.')
        if db.execute('SELECT 1 FROM recebimentos WHERE nota_id=?', (nota_id,)).fetchone():
            raise ValueError('Nota ja recebida. Estoque nao foi alterado.')
        itens = db.execute('''SELECT produto_id, quantidade, custo_unitario_centavos
            FROM itens_nota WHERE nota_id=?''', (nota_id,)).fetchall()
        if not itens:
            raise ValueError('Cadastre ao menos um item antes de receber a nota.')
        total = sum(q * custo for _, q, custo in itens)
        cursor = db.execute('''INSERT INTO recebimentos(nota_id,data_hora,total_centavos)
            VALUES (?,?,?)''', (nota_id, datetime.now(FUSO).isoformat(timespec='seconds'), total))
        recebimento_id = cursor.lastrowid
        for produto_id, quantidade, custo in itens:
            atualizou = db.execute('''UPDATE produtos SET quantidade=quantidade+?
                WHERE id=?''', (quantidade, produto_id))
            if atualizou.rowcount != 1:
                raise ValueError('Produto ausente: recebimento cancelado.')
            db.execute('''INSERT INTO movimentos_estoque
                (recebimento_id,produto_id,quantidade,custo_unitario_centavos)
                VALUES (?,?,?,?)''', (recebimento_id, produto_id, quantidade, custo))
        return total


def listar_notas():
    with conectar() as db:
        return db.execute('''SELECT n.id, n.numero, n.serie, n.emissao, f.nome,
            CASE WHEN r.id IS NULL THEN 'RASCUNHO' ELSE 'RECEBIDA' END
            FROM notas_fiscais n JOIN fornecedores f ON f.codigo=n.fornecedor_codigo
            LEFT JOIN recebimentos r ON r.nota_id=n.id ORDER BY n.id''').fetchall()


def listar_itens(nota_id):
    with conectar() as db:
        return db.execute('''SELECT p.nome, i.quantidade, i.custo_unitario_centavos
            FROM itens_nota i JOIN produtos p ON p.id=i.produto_id
            WHERE i.nota_id=? ORDER BY i.id''', (nota_id,)).fetchall()


if __name__ == '__main__':
    preparar_recebimentos()
    print('Tabelas de itens e recebimento preparadas.')

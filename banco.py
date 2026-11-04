# ETAPA 01 - SQLITE: PRODUTOS E VENDAS PERMANENTES
import sqlite3
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent / 'dados'
PASTA_DADOS.mkdir(exist_ok=True)
CAMINHO_BANCO = PASTA_DADOS / 'datacheck.db'


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO, timeout=10)
    conexao.execute('PRAGMA foreign_keys = ON')
    return conexao


def criar_banco():
    with conectar() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            preco_venda REAL NOT NULL CHECK (preco_venda > 0),
            quantidade INTEGER NOT NULL CHECK (quantidade >= 0)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            subtotal_centavos INTEGER NOT NULL CHECK (subtotal_centavos >= 0),
            descontos_centavos INTEGER NOT NULL CHECK (descontos_centavos >= 0),
            total_centavos INTEGER NOT NULL CHECK (total_centavos >= 0)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL REFERENCES vendas(id),
            produto_id INTEGER NOT NULL REFERENCES produtos(id),
            nome_produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            preco_unitario_centavos INTEGER NOT NULL CHECK (preco_unitario_centavos >= 0),
            desconto_percentual TEXT NOT NULL,
            valor_desconto_centavos INTEGER NOT NULL CHECK (valor_desconto_centavos >= 0),
            total_centavos INTEGER NOT NULL CHECK (total_centavos >= 0)
        )''')


def cadastrar_produtos():
    iniciais = [('Arroz',20.00,100),('Feijao',15.00,200),
                ('Macarrao',4.00,200),('Acucar',8.00,150),('Cafe',9.00,100)]
    with conectar() as db:
        db.executemany('''INSERT OR IGNORE INTO produtos
                (nome, preco_venda, quantidade) VALUES (?, ?, ?)''', iniciais)


def consultar_produtos():
    with conectar() as db:
        registros = db.execute('''SELECT id,nome,preco_venda,quantidade
                                  FROM produtos ORDER BY id''').fetchall()
    return registros


if __name__ == '__main__':
    criar_banco()
    cadastrar_produtos()
    for _, nome, preco, qtd in consultar_produtos():
        print(f'{nome:<12} R$ {preco:>6.2f} | estoque: {qtd}')

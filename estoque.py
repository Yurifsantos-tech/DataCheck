
# ==========================================
# DATACHECK - MODULO DE ESTOQUE
# AULA 37 - CONSULTA AO SQLITE
# ==========================================

# ETAPA 01 - IMPORTACOES

import sqlite3
from banco import CAMINHO_BANCO
from interface import titulo


# ==========================================
# ETAPA 02 - CONSULTAR ESTOQUE
# ==========================================

def mostrar_estoque():
    titulo("ESTOQUE ATUAL - SQLITE")

    with sqlite3.connect(CAMINHO_BANCO) as conexao:
        produtos = conexao.execute("""
            SELECT nome, preco_venda, quantidade
            FROM produtos
            ORDER BY id
        """).fetchall()

    print(
        f"{'PRODUTO':<12}"
        f"{'PRECO':>10}"
        f"{'QTD':>8}"
        f"{'TOTAL':>15}"
    )
    print("-" * 45)

    total_estoque = 0

    for nome, preco, quantidade in produtos:
        valor = preco * quantidade
        total_estoque += valor

        print(
            f"{nome:<12}"
            f"{preco:>10.2f}"
            f"{quantidade:>8}"
            f"{valor:>15.2f}"
        )

    print("-" * 45)
    print("TOTAL DO ESTOQUE: R$",
          f"{total_estoque:.2f}")

    while True:
        voltar = input(
            "\n[V] Voltar ao menu: "
        ).strip().upper()

        if voltar == "V":
            return

        print("Digite V para voltar.")

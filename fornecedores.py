
# ==========================================
# DATACHECK - FORNECEDORES
# INTEGRACAO COM SQLITE
# ==========================================

import sqlite3

from banco import conectar
from cadastro_db import preparar_cadastros
from interface import titulo


# ETAPA 01 - CADASTRAR FORNECEDOR

def cadastrar_fornecedor():
    titulo("CADASTRAR FORNECEDOR")

    campos = [
        ("codigo", "Codigo"),
        ("nome", "Nome"),
        ("cidade", "Cidade"),
        ("estado", "Estado"),
        ("cep", "CEP"),
        ("telefone", "Telefone"),
        ("endereco", "Endereco")
    ]

    dados = {}

    for campo, descricao in campos:
        while True:
            valor = input(
                f"{descricao} (V=voltar): "
            ).strip()

            if valor.upper() == "V":
                print("Cadastro cancelado.")
                return

            if not valor:
                print("Campo obrigatorio.")
                continue

            if campo == "estado":
                valor = valor.upper()

            dados[campo] = valor
            break

    try:
        with conectar() as db:
            db.execute("""
                INSERT INTO fornecedores
                (codigo, nome, cidade, estado,
                 cep, telefone, endereco)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["codigo"],
                dados["nome"],
                dados["cidade"],
                dados["estado"],
                dados["cep"],
                dados["telefone"],
                dados["endereco"]
            ))

        print("\nFornecedor salvo no SQLite!")

    except sqlite3.IntegrityError:
        print(
            "\nErro: codigo ja cadastrado "
            "ou dados invalidos."
        )


# ETAPA 02 - CONSULTAR FORNECEDORES

def consultar_fornecedores():
    titulo("FORNECEDORES CADASTRADOS")

    with conectar() as db:
        registros = db.execute("""
            SELECT codigo, nome, cidade,
                   estado, telefone
            FROM fornecedores
            ORDER BY nome
        """).fetchall()

    if not registros:
        print("Nenhum fornecedor cadastrado.")
    else:
        for codigo, nome, cidade, estado, telefone in registros:
            print("-" * 45)
            print("Codigo:", codigo)
            print("Nome:", nome)
            print("Cidade:", cidade)
            print("Estado:", estado)
            print("Telefone:", telefone)

    input("\nPressione Enter para voltar.")


# ETAPA 03 - MENU DE FORNECEDORES

def modulo_fornecedores():
    preparar_cadastros()

    while True:
        titulo("FORNECEDORES - SQLITE")

        print("[1] Cadastrar fornecedor")
        print("[2] Consultar fornecedores")
        print("[0] Voltar ao menu")

        opcao = input("Opcao: ").strip().upper()

        if opcao == "1":
            cadastrar_fornecedor()

        elif opcao == "2":
            consultar_fornecedores()

        elif opcao in ("0", "V"):
            return

        else:
            print("Opcao invalida!")

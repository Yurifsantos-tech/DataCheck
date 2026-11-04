# ETAPA 09 - MENU PRINCIPAL
from seguranca import verificar_estoque
from interface import titulo
from vendas import registrar_pedido
from estoque import mostrar_estoque
from fornecedores import modulo_fornecedores
from relatorios import relatorio
from notas_fiscais import modulo_entradas

def main():
    if not verificar_estoque():
        raise SystemExit("Sistema bloqueado: revise o estoque.")

    # ETAPA 12 - MENU PRINCIPAL
    while True:
        titulo("DATACHECK - GESTAO COMERCIAL")
        print("[1] PEDIDOS E VENDAS")
        print("[2] CONSULTAR ESTOQUE")
        print("[3] FORNECEDORES")
        print("[4] RELATORIOS")
        print("[5] ENTRADA DE MERCADORIAS")
        print("[0] SAIR")
        print("-" * 48)
        opcao = input("Escolha uma opcao: ").strip()
        if opcao == "1":
            registrar_pedido()
        elif opcao == "2":
            mostrar_estoque()
        elif opcao == "3":
            modulo_fornecedores()
        elif opcao == "4":
            relatorio()
        elif opcao == "5":
            modulo_entradas()
        elif opcao == "0":
            print("Sistema encerrado.")
            break
        else:
            print("Opcao invalida!")

if __name__ == "__main__":
    main()

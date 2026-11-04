# ETAPA 02 - FORMATACAO E NAVEGACAO

def titulo(texto):
    print("\n" + "=" * 48)
    print(texto.center(48))
    print("=" * 48)

def dinheiro(valor):
    return f"R$ {valor:.2f}"

def aguardar_voltar():
    while input("\n[V] Voltar ao menu: ").strip().upper() != "V":
        print("Digite V para voltar.")

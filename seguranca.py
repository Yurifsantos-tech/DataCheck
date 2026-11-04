# ETAPA 03 - BARREIRA DE INTEGRIDADE
from math import isfinite
from dados import estoque

def verificar_estoque():
    nomes = set()
    for item in estoque:
        if not isinstance(item, list) or len(item) != 3:
            print("ERRO: estrutura do produto invalida!")
            return False
        nome, preco, quantidade = item
        if not isinstance(nome, str) or not nome.strip():
            print("ERRO: nome invalido!")
            return False
        normalizado = nome.strip().casefold()
        if normalizado in nomes:
            print("ERRO: produto duplicado!")
            return False
        nomes.add(normalizado)
        if type(preco) not in (int, float) or not isfinite(preco) or preco <= 0:
            print("ERRO: preco invalido!")
            return False
        if type(quantidade) is not int or quantidade < 0:
            print("ERRO: quantidade de estoque invalida!")
            return False
    return True

# ETAPA 01 - DADOS COMPARTILHADOS (EM MEMORIA)
from datetime import timezone, timedelta
FUSO = timezone(timedelta(hours=-3))
estoque = [
    ["Arroz", 20.00, 100],
    ["Feijao", 15.00, 200],
    ["Macarrao", 4.00, 200],
    ["Acucar", 8.00, 150],
    ["Cafe", 9.00, 100],
]
fornecedores = []
vendas = []
notas_fiscais = []

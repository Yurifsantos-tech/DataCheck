"""Aulas 40/41: tabelas persistentes de fornecedores e rascunhos de NF."""
from banco import conectar, criar_banco


def preparar_cadastros():
    criar_banco()
    with conectar() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS fornecedores (
            codigo TEXT PRIMARY KEY,
            nome TEXT NOT NULL CHECK(length(trim(nome)) > 0),
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            cep TEXT NOT NULL,
            telefone TEXT NOT NULL,
            endereco TEXT NOT NULL
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS notas_fiscais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            serie TEXT NOT NULL,
            emissao TEXT NOT NULL,
            fornecedor_codigo TEXT NOT NULL REFERENCES fornecedores(codigo),
            situacao TEXT NOT NULL DEFAULT 'RASCUNHO'
                CHECK(situacao = 'RASCUNHO'),
            UNIQUE(numero, serie, fornecedor_codigo)
        )''')


if __name__ == '__main__':
    preparar_cadastros()
    print('Tabelas de fornecedores e notas fiscais preparadas.')

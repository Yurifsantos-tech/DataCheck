# 📦 DataCheck — Sistema de Gestão Comercial em Python

Projeto acadêmico desenvolvido para aplicar conhecimentos de lógica de programação, Python, banco de dados e desenvolvimento de software.

O DataCheck é um sistema demonstrativo de gestão comercial com interface gráfica desenvolvida em Streamlit e persistência de dados em SQLite.

## Funcionalidades

- Painel inicial com indicadores de vendas, estoque, fornecedores e notas fiscais.
- Registro de vendas com quantidades e descontos por produto.
- Atualização do estoque após vendas confirmadas.
- Consulta de produtos, preços e quantidades disponíveis.
- Cadastro e consulta de fornecedores.
- Cadastro de notas fiscais, inclusão de itens e confirmação de recebimento.
- Atualização do estoque mediante recebimento de mercadorias.
- Relatórios resumidos de vendas recentes e estoque.
- Autenticação administrativa local para operações na interface visual.
- Testes automatizados de operações selecionadas.

## Tecnologias utilizadas

- **Python:** linguagem principal do projeto.
- **Streamlit:** interface gráfica acessada pelo navegador.
- **SQLite:** armazenamento persistente dos dados.
- **SQL:** criação, consulta e atualização de registros.
- **unittest:** testes automatizados.
- **VS Code:** ambiente de desenvolvimento.

## Como executar localmente

Requisitos: Python 3 e acesso a um terminal.

Clone o repositório e entre na pasta do projeto.

Crie um ambiente virtual:

```bash
python3 -m venv .venv
```

Ative o ambiente no macOS ou Linux:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Prepare o banco de dados local:

```bash
python banco.py
python cadastro_db.py
python recebimento_db.py
```

Configure uma senha administrativa local:

```bash
python seguranca_admin.py
```

Inicie a interface:

```bash
python -m streamlit run app_visual_datacheck_revisado.py
```

Abra o endereço local indicado no terminal.

**Observação:** o banco de dados e a configuração administrativa não são distribuídos no repositório. Cada instalação deve criar seus próprios arquivos locais.

## Estrutura principal

- `app_visual_datacheck_revisado.py` — interface visual.
- `banco.py` — conexão SQLite e estrutura inicial.
- `cadastro_db.py` — tabelas de fornecedores e notas fiscais.
- `recebimento_db.py` — operações de recebimento.
- `operacoes_visual.py` — operações comerciais utilizadas pela interface.
- `seguranca_admin.py` — autenticação administrativa local.
- `testes_datacheck.py` — testes automatizados.

## Testes

Para executar os testes incluídos no projeto:

```bash
python -m unittest -v testes_datacheck.py teste_isolado_49.py
```

Os testes automatizados cobrem cenários selecionados e não representam uma validação integral do sistema.

## Limitações

O DataCheck é um projeto acadêmico e demonstrativo, não um produto comercial pronto para produção.

- A autenticação foi desenvolvida para uso local.
- Os relatórios apresentam consultas resumidas, não um histórico financeiro completo.
- Ainda existem melhorias planejadas para usabilidade, relatórios e validações.
- A interface não deve ser publicada diretamente na internet sem uma revisão de segurança.

## Próximas melhorias

- Detalhamento dos itens de cada venda.
- Relatórios completos com filtros e exportação.
- Aperfeiçoamento de mensagens e elementos visuais.
- Ampliação dos testes automatizados.
- Melhorias no gerenciamento de fornecedores e nas permissões.

## Objetivo educacional

O projeto demonstra a aplicação prática de funções, estruturas de decisão, laços, modularização, validação de dados, operações SQL, transações e testes.

Desenvolvido como parte de uma trajetória de aprendizagem em Python e Engenharia de Software, com apoio de ferramentas de inteligência artificial na orientação, revisão e depuração do código.
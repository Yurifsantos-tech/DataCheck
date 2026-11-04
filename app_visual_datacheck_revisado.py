"""DataCheck: interface visual renovada, preservando operações da Aula 49."""
import sqlite3
from datetime import datetime
from decimal import Decimal
import streamlit as st
from banco import conectar, consultar_produtos, CAMINHO_BANCO
from cadastro_db import preparar_cadastros
from recebimento_db import cadastrar_nota, adicionar_item, receber_nota, listar_notas, listar_itens, preparar_recebimentos
from seguranca_admin import autenticar, ARQUIVO
from operacoes_visual import cadastrar_fornecedor, registrar_venda

st.set_page_config(page_title='DataCheck | Gestão Comercial', page_icon='📦', layout='wide')
st.markdown("""<style>
[data-testid="stAppViewContainer"] {background: #f5f8fd;}
[data-testid="stSidebar"] {background:#152d4e; min-width:255px;}
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] p,[data-testid="stSidebar"] label {color:#f3f7ff !important;}
[data-testid="stSidebar"] div[role="radiogroup"] label {border-radius:10px; padding:9px 12px; transition:background .15s;}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {background:#24446e;}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {background:#245da9;}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {color:white!important;}
[data-testid="stSidebar"] button {background:#e7f0ff!important;color:#18385d!important;}
[data-testid="stSidebar"] input {color:#142b4c!important;}
[data-testid="stSidebar"] [data-testid="stForm"] {background:#223d61!important;border:1px solid #456184!important;padding:14px!important;}
[data-testid="stSidebar"] [data-testid="stForm"] label,
[data-testid="stSidebar"] [data-testid="stForm"] label p {color:#f8fafc!important;opacity:1!important;}
[data-testid="stSidebar"] [data-testid="stForm"] input {background:#fff!important;color:#162a48!important;-webkit-text-fill-color:#162a48!important;}
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button {background:#2a78e0!important;color:#fff!important;border:0!important;font-weight:700!important;}
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button:hover {background:#175cb6!important;}
[data-testid="stSidebar"] [data-testid="stAlert"] p {color:#122442!important;}
/* Cartões de ações: o botão é o controle clicável, não um ornamento separado. */
[class*="st-key-quick_"] {border-radius:14px;padding:16px 11px 12px;border:1px solid #d9e4f3;min-height:145px;}
[class*="st-key-quick_"] [data-testid="stButton"] button {width:100%;min-height:55px;border:0!important;background:transparent!important;color:#142848!important;font-weight:800!important;white-space:normal!important;text-align:left!important;box-shadow:none!important;}
[class*="st-key-quick_"] [data-testid="stButton"] button:hover {background:#ffffff80!important;}
[class*="st-key-quick_"] p {color:#526783!important;font-size:.83rem!important;}
.st-key-quick_Vendas{background:#ecfbf3;border-color:#b8ebd0}
.st-key-quick_Estoque{background:#edf5ff;border-color:#c6dcff}
.st-key-quick_Fornecedores{background:#f4efff;border-color:#dfd0ff}
.st-key-quick_Notas_fiscais{background:#fff9e9;border-color:#fae3ad}
.st-key-quick_Relatorios{background:#f2f5fa;border-color:#d9e1eb}

.block-container {max-width:1370px; padding-top:1.5rem; padding-bottom:3rem;}
h1,h2,h3 {color:#122442;letter-spacing:-.018em;}
h1 {font-size:2.0rem!important;}
[data-testid="stForm"], [data-testid="stExpander"] {border-radius:15px;background:white;border:1px solid #e3eaf4;padding:12px;}
[data-testid="stDataFrame"] {border-radius:12px;overflow:hidden;}
.dc-topbar {display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #dfe8f3; padding:0 0 14px; margin-bottom:14px; color:#5c6d85; font-size:0.91rem;}
.dc-panel {background:#fff;border:1px solid #e2eaf4;border-radius:16px;padding:20px;margin-top:6px;box-shadow:0 4px 16px rgba(21,46,79,.025);}
.dc-metric {border:1px solid var(--dc-border);background:var(--dc-bg);border-radius:15px;min-height:126px;padding:19px 16px;margin-bottom:5px;}
.dc-metric .dc-icon {font-size:1.5rem;float:left;margin-right:11px;}
.dc-metric .dc-label {font-size:.85rem;color:#435875;font-weight:650;line-height:1.35;}
.dc-metric .dc-value {font-weight:760;font-size:1.55rem;color:#132849;margin-top:8px;white-space:nowrap;}
.dc-metric .dc-detail {font-size:.8rem;color:#6b7c90;margin-top:3px;}
.dc-intro {font-size:.98rem;color:#657792;margin:-.35rem 0 1.1rem;}
.dc-section {font-size:1.16rem;font-weight:750;color:#142848;margin:.3rem 0 .8rem;}
.dc-cardtop {font-size:1.05rem;font-weight:700;color:#173455;margin-bottom:10px;}
.dc-action {min-height:112px;padding:16px 13px 5px;border-radius:14px;border:1px solid var(--dc-border);background:var(--dc-bg);}
.dc-action .emoji {font-size:1.4rem;margin-bottom:7px;}
.dc-action .name {font-weight:750;color:#173455;font-size:.94rem;}
.dc-action .desc {font-size:.78rem;color:#60718a;margin-top:4px;}
/* Os botoes logo abaixo dos blocos são os controles reais de navegação. */
[data-testid="stButton"] button {border-radius:10px;}
[data-testid="stMetric"] {background:white;padding:16px;border-radius:12px;border:1px solid #e4eaf2;}
</style>""",unsafe_allow_html=True)

def moeda_centavos(c):
    return 'R$ ' + f'{c/100:,.2f}'.replace(',','X').replace('.',',').replace('X','.')

def moeda(valor):
    return 'R$ ' + f'{valor:,.2f}'.replace(',','X').replace('.',',').replace('X','.')

def ler(sql, params=()):
    with conectar() as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute(sql,params).fetchall()]

def erro_exc(erro):
    st.error(f'Operação não realizada: {erro}')

if 'autorizado' not in st.session_state:
    st.session_state.autorizado = False
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = {}

st.sidebar.markdown('## 📦 DataCheck')
st.sidebar.caption('Gestão Comercial · Painel de trabalho')
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 'Início'
paginas = ['Início', 'Vendas', 'Estoque', 'Fornecedores', 'Notas fiscais', 'Relatórios', 'Administração']
def navegar_para(destino):
    # Callback executado antes da criacao do radio na proxima execucao.
    st.session_state['pagina_atual'] = destino

pagina = st.sidebar.radio('Navegação', paginas, key='pagina_atual')
st.sidebar.divider()
if ARQUIVO.is_file():
    if st.session_state.autorizado:
        st.sidebar.success('Administrador autenticado nesta sessão')
        if st.sidebar.button('Sair da administração'):
            st.session_state.autorizado = False
            st.rerun()
    else:
        with st.sidebar.form('login'):
            senha = st.text_input('Senha administrativa', type='password')
            entrar = st.form_submit_button('Autorizar operações')
        if entrar:
            if autenticar(senha):
                st.session_state.autorizado = True
                st.rerun()
            else:
                st.sidebar.error('Senha incorreta.')
else:
    st.sidebar.warning('Configure a senha antes: python3 seguranca_admin.py')
st.sidebar.caption('Não publique esta interface na internet: login demonstrativo local.')
st.markdown(f'<div class="dc-topbar"><span>📦 DataCheck · Gestão Comercial</span><span>📅 {datetime.now():%d/%m/%Y %H:%M} &nbsp; · &nbsp; {"Administrador autorizado" if st.session_state.autorizado else "Consulta / acesso restrito"}</span></div>', unsafe_allow_html=True)
if not CAMINHO_BANCO.exists():
    st.error('Banco não encontrado. Verifique a pasta dados/datacheck.db.')
    st.stop()
try:
    produtos = consultar_produtos()
except sqlite3.Error as e:
    erro_exc(e); st.stop()

if pagina == 'Início':
    st.title('Painel Inicial')
    st.markdown('<div class="dc-intro">Visão geral e acesso rápido. Cada operação tem sua própria tela.</div>', unsafe_allow_html=True)
    total_unidades = sum(int(p[3]) for p in produtos)
    fornecedores_total = ler('SELECT COUNT(*) AS n FROM fornecedores')[0]['n']
    notas_total = ler('SELECT COUNT(*) AS n FROM notas_fiscais')[0]['n']
    registros = ler('SELECT data_hora, total_centavos FROM vendas ORDER BY id DESC')
    hoje = datetime.now().date()
    vendas_hoje = 0
    valor_hoje = 0
    serie = {}
    from datetime import timedelta
    for reg in registros:
        try:
            data_venda = datetime.fromisoformat(str(reg['data_hora']).replace('Z', '+00:00')).date()
        except (ValueError, TypeError):
            continue
        if hoje - timedelta(days=6) <= data_venda <= hoje:
            chave = data_venda.strftime('%d/%m')
            serie[chave] = serie.get(chave, 0) + int(reg['total_centavos']) / 100
        if data_venda == hoje:
            vendas_hoje += 1
            valor_hoje += int(reg['total_centavos'])

    def cartao(icone, rotulo, valor, detalhe, cor, borda):
        st.markdown(f'<div class="dc-metric" style="--dc-bg:{cor};--dc-border:{borda}"><div class="dc-icon">{icone}</div><div class="dc-label">{rotulo}</div><div class="dc-value">{valor}</div><div class="dc-detail">{detalhe}</div></div>', unsafe_allow_html=True)

    col1,col2,col3,col4 = st.columns(4, gap='small')
    with col1: cartao('🛒','Vendas de hoje',moeda_centavos(valor_hoje),f'{vendas_hoje} venda(s) registrada(s)','#effcf6','#d5f0e5')
    with col2: cartao('📦','Unidades em estoque',str(total_unidades),f'{len(produtos)} produtos cadastrados','#eff6ff','#d7e6ff')
    with col3: cartao('📄','Notas fiscais',str(notas_total),'Documentos cadastrados','#fff9eb','#fae8bd')
    with col4: cartao('👥','Fornecedores',str(fornecedores_total),'Cadastros existentes','#f5f1ff','#e5dbff')

    coluna_grafico, coluna_estoque = st.columns([1.35, 1], gap='medium')
    with coluna_grafico:
        st.markdown('<div class="dc-section">📊 Vendas dos últimos 7 dias</div>', unsafe_allow_html=True)
        with st.container(border=True):
            dias = [hoje-timedelta(days=i) for i in range(6,-1,-1)]
            valores = {d.strftime('%d/%m'): serie.get(d.strftime('%d/%m'),0) for d in dias}
            if any(v > 0 for v in valores.values()):
                st.line_chart(valores, height=252, color='#1874e8')
            else:
                st.info('Sem vendas registradas nos últimos 7 dias. O gráfico aparecerá com as primeiras vendas confirmadas.')
                st.caption('O gráfico será exibido quando houver vendas reais no SQLite.')
    with coluna_estoque:
        st.markdown('<div class="dc-section">📦 Estoque em destaque</div>', unsafe_allow_html=True)
        with st.container(border=True):
            destacados = sorted(produtos, key=lambda p:int(p[3]))[:5]
            st.dataframe([{'Produto':p[1],'Estoque':p[3],'Situação': '🔴 Sem estoque' if p[3]==0 else ('🟠 Atenção' if p[3]<=10 else '🟢 Normal')} for p in destacados], hide_index=True, use_container_width=True, height=251)
            st.caption('Atenção: limite demonstrativo de até 10 unidades.')

    st.markdown('<div class="dc-section">⚡ Acesso rápido</div>', unsafe_allow_html=True)
    atalhos = [
        ('🛒','Nova venda','Registrar pedido','Vendas','#edfbf4','#cdeedb'),
        ('📦','Consultar estoque','Ver produtos e saldos','Estoque','#eff6ff','#d1e3ff'),
        ('👥','Fornecedores','Cadastros e consultas','Fornecedores','#f5f0ff','#e2d8ff'),
        ('📄','Notas fiscais','Entradas e recebimentos','Notas fiscais','#fff9e9','#f6e5ba'),
        ('📊','Relatórios','Vendas e estoque','Relatórios','#f2f5fa','#dee5f0'),
    ]
    for coluna, (icone, nome, detalhe, destino, fundo, borda) in zip(st.columns(5, gap='small'), atalhos):
        with coluna:
            with st.container(key='quick_' + destino.replace(' ', '_').replace('ó', 'o')):
                st.button(f'{icone}  {nome}  →', key=f'atalho_{destino}',
                          use_container_width=True, on_click=navegar_para, args=(destino,))
                st.caption(detalhe)
    st.caption('Painel baseado exclusivamente nos dados registrados no SQLite. Acesso local de demonstração.')

elif pagina == 'Estoque':
    st.subheader('Consulta de estoque')
    st.dataframe([{'ID':p[0],'Produto':p[1],'Quantidade':p[3],'Preço de venda':moeda(p[2])} for p in produtos], hide_index=True, use_container_width=True)
    st.info('Alterações de estoque ocorrem apenas por venda confirmada ou recebimento de nota.')

elif pagina == 'Fornecedores':
    st.subheader('Fornecedores')
    st.dataframe(ler('SELECT codigo AS Código,nome AS Nome,cidade AS Cidade,estado AS UF,cep AS CEP,telefone AS Telefone,endereco AS Endereço FROM fornecedores ORDER BY nome'),hide_index=True,use_container_width=True)
    if st.session_state.autorizado:
        with st.expander('Cadastrar fornecedor'):
            with st.form('fornecedor',clear_on_submit=True):
                a,b=st.columns(2)
                codigo=a.text_input('Código*'); nome=b.text_input('Nome*')
                cidade=a.text_input('Cidade*'); estado=b.text_input('UF*')
                cep=a.text_input('CEP*'); telefone=b.text_input('Telefone*')
                endereco=st.text_input('Endereço*')
                enviar=st.form_submit_button('Salvar fornecedor')
            if enviar:
                try:
                    cadastrar_fornecedor(codigo,nome,cidade,estado,cep,telefone,endereco)
                    st.success('Fornecedor registrado no SQLite.');st.rerun()
                except (ValueError,sqlite3.Error) as e: erro_exc(e)
    else: st.info('Autentique-se na barra lateral para cadastrar fornecedores.')

elif pagina == 'Notas fiscais':
    st.subheader('Notas fiscais e entradas')
    notas = listar_notas()
    st.dataframe([{'ID':n[0],'Número':n[1],'Série':n[2],'Emissão':n[3],'Fornecedor':n[4],'Situação':n[5]} for n in notas],hide_index=True,use_container_width=True)
    if notas:
        ids = [int(n[0]) for n in notas]
        id_nf = st.selectbox('Nota selecionada (ID interno)',ids,format_func=lambda i: next(f'ID {n[0]} · NF {n[1]}/{n[2]} · {n[5]}' for n in notas if n[0]==i))
        linhas = listar_itens(id_nf)
        st.dataframe([{'Produto':nome,'Quantidade':qtd,'Custo unitário':moeda_centavos(cents),'Subtotal':moeda_centavos(qtd*cents)} for nome,qtd,cents in linhas],hide_index=True,use_container_width=True)
        st.markdown(f'**Total da nota: {moeda_centavos(sum(q*c for _,q,c in linhas))}**')
    else: id_nf=None
    if not st.session_state.autorizado:
        st.info('Autentique-se na barra lateral para cadastrar itens e confirmar recebimentos.')
    else:
        tabs = st.tabs(['Criar rascunho','Adicionar item','Confirmar recebimento'])
        with tabs[0]:
            fornecedores=ler('SELECT codigo,nome FROM fornecedores ORDER BY nome')
            with st.form('criar_nf'):
                numero=st.text_input('Número da NF')
                serie=st.text_input('Série',value='1')
                emissao=st.date_input('Data de emissão',max_value=datetime.now().date())
                cod=st.selectbox('Fornecedor', [f['codigo'] for f in fornecedores],format_func=lambda x:next(f['nome'] for f in fornecedores if f['codigo']==x)) if fornecedores else None
                confirmar=st.form_submit_button('Criar nota em rascunho',disabled=not bool(fornecedores))
            if confirmar:
                try:
                    if not numero.isdigit() or int(numero)<=0 or not serie.isdigit(): raise ValueError('Número e série devem ser numéricos.')
                    nid=cadastrar_nota(numero,serie,emissao.strftime('%d/%m/%Y'),cod)
                    st.success(f'Nota criada com ID interno {nid}.');st.rerun()
                except (ValueError,sqlite3.Error) as e: erro_exc(e)
        with tabs[1]:
            if id_nf is not None:
                if next(n[5] for n in notas if n[0]==id_nf)=='RECEBIDA':
                    st.warning('Esta nota já foi recebida e não pode receber mais itens.')
                else:
                    with st.form('item_nf'):
                        pid=st.selectbox('Produto',[p[0] for p in produtos],format_func=lambda i:next(p[1] for p in produtos if p[0]==i))
                        qtd=st.number_input('Quantidade recebida',min_value=1,step=1,value=1)
                        custo=st.text_input('Custo unitário de compra (ex.: 14,00)')
                        ok=st.form_submit_button('Adicionar item ao rascunho')
                    if ok:
                        try:
                            adicionar_item(id_nf,pid,int(qtd),custo)
                            st.success('Item salvo. Estoque não alterado.');st.rerun()
                        except (ValueError,sqlite3.Error) as e: erro_exc(e)
        with tabs[2]:
            if id_nf is not None:
                situacao=next(n[5] for n in notas if n[0]==id_nf)
                if situacao=='RECEBIDA': st.info('Nota já recebida. Não confirmar novamente.')
                elif not listar_itens(id_nf): st.warning('Nota sem itens.')
                else:
                    st.warning('Esta ação aumenta o estoque de forma permanente. Confira os itens acima.')
                    with st.form('receber_nf'):
                        confirmacao=st.checkbox('Conferi os itens e desejo registrar o recebimento definitivo.')
                        btn=st.form_submit_button('Confirmar recebimento')
                    if btn and not confirmacao:
                        st.error('Marque a confirmação antes de receber.')
                    elif btn:
                        try:
                            total=receber_nota(id_nf)
                            st.success(f'Recebimento concluído: {moeda_centavos(total)}.');st.rerun()
                        except (ValueError,sqlite3.Error) as e: erro_exc(e)

elif pagina == 'Vendas':
    st.subheader('Vendas')
    vendas=ler('SELECT id,data_hora,total_centavos FROM vendas ORDER BY id DESC LIMIT 100')
    st.dataframe([{'Pedido':v['id'],'Data':v['data_hora'],'Total':moeda_centavos(v['total_centavos'])} for v in vendas],hide_index=True,use_container_width=True)
    if not st.session_state.autorizado: st.info('Autentique-se na barra lateral para fazer vendas.')
    else:
        st.subheader('Novo pedido')
        with st.form('montar_venda'):
            itens=[]
            for pid,nome,preco,estoque in produtos:
                a,b,c=st.columns([3,2,2])
                a.write(f'{nome} · {moeda(preco)} · estoque: {estoque}')
                quantidade=b.number_input(f'Qtd. {nome}', min_value=0, max_value=int(estoque), step=1,key=f'q_{pid}')
                desconto=c.selectbox(f'Desc. {nome}', ['0','1','1.5','2','2.5','3'],key=f'd_{pid}')
                if quantidade: itens.append((pid,int(quantidade),desconto))
            preparar=st.form_submit_button('Preparar pedido')
        if preparar:
            st.session_state.carrinho = {x[0]:(x[1],x[2]) for x in itens}
        if st.session_state.carrinho:
            st.warning('Revise os itens antes de confirmar. A venda reduzirá o estoque.')
            st.dataframe([{'Produto':next(p[1] for p in produtos if p[0]==pid),'Quantidade':q,'Desconto %':d} for pid,(q,d) in st.session_state.carrinho.items()],hide_index=True)
            with st.form('confirmar_venda'):
                conf=st.checkbox('Confirmo a venda e a baixa no estoque')
                salvar=st.form_submit_button('Registrar venda')
            if salvar and not conf:
                st.error('Marque a confirmação antes de registrar a venda.')
            elif salvar:
                try:
                    venda_id,total=registrar_venda([(pid,q,d) for pid,(q,d) in st.session_state.carrinho.items()])
                    st.session_state.carrinho={}
                    st.success(f'Venda #{venda_id} registrada: {moeda_centavos(total)}');st.rerun()
                except (ValueError,sqlite3.Error) as e: erro_exc(e)
            if st.button('Cancelar pedido'): st.session_state.carrinho={};st.rerun()

elif pagina == 'Relatórios':
    st.header('Relatórios')
    st.caption('Consultas resumidas. Não representam um histórico completo de todas as movimentações.')
    resumo_vendas=ler('SELECT id, data_hora, total_centavos FROM vendas ORDER BY id DESC LIMIT 100')
    total_vendas=sum(int(v['total_centavos']) for v in resumo_vendas)
    x,y=st.columns(2)
    x.metric('Vendas exibidas',len(resumo_vendas))
    y.metric('Total das vendas exibidas',moeda_centavos(total_vendas))
    t1,t2=st.tabs(['Vendas recentes','Estoque atual'])
    with t1:
        st.dataframe([{'Venda':v['id'],'Data':v['data_hora'],'Total':moeda_centavos(v['total_centavos'])} for v in resumo_vendas],hide_index=True,use_container_width=True)
        st.caption('Consulta limitada às 100 vendas mais recentes.')
    with t2:
        st.dataframe([{'Produto':p[1],'Unidades':p[3],'Preço de venda':moeda(p[2])} for p in produtos],hide_index=True,use_container_width=True)

elif pagina == 'Administração':
    st.subheader('Controle administrativo')
    st.write('Proteção por senha local na interface visual, para as operações de escrita.')
    st.warning('Esta proteção não restringe o uso de main.py no terminal. Não exponha o servidor Streamlit em rede pública.')
    st.caption('Faça backups periódicos usando python3 backup_sqlite.py, com o aplicativo fechado.')
    st.caption('Controle de permissões por usuário ainda não implementado. Somente autenticação administrativa local de demonstração.')

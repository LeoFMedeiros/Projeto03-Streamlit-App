import streamlit as st
import pandas as pd
import fundamentus as fd # Biblioteca do site Fundamentus
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

def baixar_cotacoes_acoes(ativos):
    time = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    acoes = yf.download(ativos, period='3y')['Adj Close']
    acoes = acoes.pct_change().dropna()
    acoes = acoes[acoes.index <= time]
    return acoes


def matrix_seriation(retornos):

  matriz_covarianca = retornos.cov()

  dendograma = sns.clustermap(matriz_covarianca, method='ward', metric='euclidean')

  colunas_seriation = dendograma.dendrogram_col.reordered_ind
  colunas_seriation = retornos.columns[colunas_seriation]

  return (matriz_covarianca, colunas_seriation)

def calcula_pesos_hrp(matriz_cov, colunas_seriation):
    # Inicialização de pesos
    pesos = pd.Series(1, index=colunas_seriation)
    paridades = [colunas_seriation]

    while len(paridades) > 0:
        # Instanciação de clusters
        paridades = [cluster[inicio:fim] 
                     for cluster in paridades
                      for inicio, fim in ((0, len(cluster) // 2),(len(cluster) // 2, len(cluster)))
                        if len(cluster) > 1]

        # Iteração entre paridades
        for subcluster in range(0, len(paridades), 2):
            
            cluster_esquerdo = paridades[subcluster]
            cluster_direito = paridades[subcluster + 1]
            
            matriz_cov_esquerda = matriz_cov[cluster_esquerdo].loc[cluster_esquerdo]
            inversa_diagonal = 1 / np.diag(matriz_cov_esquerda.values)
            pesos_cluster_esquerdo = inversa_diagonal / np.sum(inversa_diagonal)
            vol_cluster_esquerdo = np.dot(pesos_cluster_esquerdo, np.dot(matriz_cov_esquerda, pesos_cluster_esquerdo))

            matriz_cov_direita = matriz_cov[cluster_direito].loc[cluster_direito]
            inversa_diagonal = 1 / np.diag(matriz_cov_direita.values)
            pesos_cluster_direito = inversa_diagonal  / np.sum(inversa_diagonal)
            vol_cluster_direito = np.dot(pesos_cluster_direito, np.dot(matriz_cov_direita, pesos_cluster_direito))

            fator_alocacao = 1 - vol_cluster_esquerdo / (vol_cluster_esquerdo + vol_cluster_direito)

            pesos[cluster_esquerdo] *= fator_alocacao
            pesos[cluster_direito] *= 1 - fator_alocacao
            
    return pesos

def back_testing(tickers_IBOV, pesos, valor):

    simulacao = yf.download(tickers_IBOV, period='1y')['Adj Close']
    simulacao = simulacao.pct_change().dropna()

    #VOLATILIDADE DA CARTEIRA
    pesos_vol = pd.DataFrame(pesos)
    cov_matrix = simulacao.cov()
    vol_ano = np.sqrt(np.dot(pesos_vol.T, np.dot(cov_matrix,pesos_vol)))*np.sqrt(252)

    pesos_iguais = simulacao.copy()

    ibov = yf.download('^BVSP', period='1y')['Adj Close']
    ibov = ibov.pct_change().dropna().cumsum()

    lista = simulacao.columns
    for tick in lista:
        simulacao[tick] = simulacao[tick] * pesos[tick]
    simulacao['retorno'] = simulacao.sum(axis=1)
    simulacao['retorno_anual'] = simulacao['retorno'].cumsum()

    for tick in lista:
        pesos_iguais[tick] = pesos_iguais[tick] * (1/len(tickers_IBOV))
    pesos_iguais['retorno'] = pesos_iguais.sum(axis=1)
    pesos_iguais['retorno_anual'] = pesos_iguais['retorno'].cumsum()
    
    # SHARPE RATIO
    selic = 0.1375
    sharpe_ratio = ((simulacao['retorno'].mean()*252)-selic)/(vol_ano)

    # RETORNO DA CARTEIRA
    tamanho = len(simulacao) - 1
    retorno_da_carteira =  simulacao.iloc[-1]['retorno_anual']

    # MAXIXMO DRAWDOWN DA CARTEITA
    pico = simulacao['retorno_anual'].expanding(min_periods=1).max()
    dd = (simulacao['retorno_anual']/pico)-1
    drawdown = dd.min()

    # VALUE AT RISK
    var_95 = np.nanpercentile(simulacao['retorno'],5)

    #plt.figure(figsize=(12,8))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ibov.index, y=ibov,
                    mode='lines', name='IBOV'))
    fig.add_trace(go.Scatter(x=simulacao.index, y=simulacao.retorno_anual,
                    mode='lines',name='CARTEIRA'))
    fig.add_trace(go.Scatter(x=pesos_iguais.index, y=pesos_iguais.retorno_anual,
                    mode='lines',name='CARTEIRA DE PESOS IGUAIS'))
    #fig.show()

    # DIVIDENDOS RECEBIDS
    qtd_de_acoes = yf.download(tickers_IBOV, period='1y')['Close']
    primeiro_dia = qtd_de_acoes.index.min().strftime('%Y-%m-%d')
    #print(primeiro_dia)
    qtd_de_acoes = qtd_de_acoes[qtd_de_acoes.index == primeiro_dia]

    lista = qtd_de_acoes.columns
    for tick in lista:
        qtd_de_acoes[tick] = ((pesos[tick] * valor)/(qtd_de_acoes[tick]))

    dividendos_recebidos = 0
    for tick in lista:
        try:
            dividendos_recebidos += (yf.Ticker(tick).history(start=primeiro_dia)['Dividends'].sum() * qtd_de_acoes[tick][0])
        except:
            print('erro')
            continue

    return [fig, vol_ano, drawdown, sharpe_ratio, retorno_da_carteira, dividendos_recebidos, qtd_de_acoes]

def quantidade_de_acoes_para_comprar(ativos, valor, pesos):
    acoes = yf.download(ativos, period='1y')['Close']
    acoes = acoes.iloc[-1]
    for tick in ativos:
        acoes[tick] = ((pesos[tick] * valor)/(acoes[tick]))
    return acoes



def apresentacao():
    # PARTE SUPEIOR DA PÁGINA DE APRESENTAÇÃO DO AUTOR
    col1, col2 = st.columns([1,3])

    # COLUNA 1 DE IMAGEM DO AUTOR
    with col1:
        st.markdown('')
        st.markdown('')
        st.image('leonardo_capa.jpg')
    
    # INFORMAÇÕES DO AUTOR
    with col2:
        st.title('Leonardo Medeiros')
        st.markdown('''
        Idade: 24 anos\n
        Profissão: Cientista de Dados\n
        Formação: Engenharia Química UFRN **(EM FORMAÇÃO)**
        ''')
    st.markdown('---')

    # INFORMAÇÕES SOBRE O AUTOR
    st.markdown('''
    Atuo na área de dados há mais de 1 ano, no Grupo Aerotur, como Cientista de Dados. Por meio dessa experiência, consegui desenvolver bastante o meu conhecimento em python para elaboração de automações, análise de dados, web scraping, machine learning e desenvolvimento de dashboard com a biblioteca DASH. Além disso, também adquiri uma gama de conhecimentos em ETL e SQL.

    Atualmente estou no último período do curso de Engenharia Química da URFN, no qual participei por 2 anos do Centro Acadêmico do curso e por 8 meses da empresa jr (NutEQ), realizando projetos e trabalhando no setor de RH, além da realização de projeto de extensão como voluntário.

    No meu tempo livre gosto de assistir, jogar video game, praticar vôlei, estudar programação e realizar projetos pessoais com o uso da linguagem python. Dentre esses projetos, vale destacar:
    - Bot do telegram para baixar músicas do YouTube e disponibilizar em um app.
    - Criação de um robô de apostas de futebol.
    ''', )
    st.markdown('---')

    # HABILIDADES 
    st.subheader('Habilidades')   
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('''
        :white_check_mark:  Python

        :white_check_mark:  SQL

        :white_check_mark:  Web Scraping
        ''')

    with col2:
        st.markdown('''
        :white_check_mark:  HTML | CSS

        :white_check_mark:  DASH PLOTLY

        :white_check_mark:  STREAMLIT
        ''')

    with col3:
        st.markdown('''
        :white_check_mark:  Automações

        :white_check_mark:  Machine Learning

        :white_check_mark:  Data Studio
        ''')
    st.markdown('---')

    # PROJETOS REALIZADOS
    st.subheader('Projetos Realizados')

    st.markdown('''
    - DASHBOARDS COM DATA STUDIO + AUTOMAÇÃO

    - CRIAÇÃO DE SISTEMA PARA ENVIOS DE RELATÓRIOS AUTOMÁTICOS E ARMAZENAMENTO DE DADOS COM PYTHON.

    - APRENDIZAGEM DE MÁQUINA NÃO SUPERVISIONADA PARA ANÁLISE DE CLIENTES

    - FORECAST DE PROJEÇÃO DE VENDAS NO MÊS

    - WEB SCRAPING DE MONITORAMENTO DE PREÇOS

    - MINI APP E CONSTRUÇÃO DASHBOARDS COM PYTHON - BIBLIOTECA DASH E STREAMLIT

    - ROBÔ DE APOSTAS ESPORTIVAS USANDO APRENDIZAGEM DE MÁQUINA SUPERVISIONADA
    ''')



def futebol():
    # TÍTULO DA PÁGINA
    st.title('ANÁLISE DE TIMES')
    st.subheader('A fonte de dados utilizada na construção desse relatório foi pelo site: https://www.football-data.co.uk \n\n- Ultima atualização: 27/11/2022')
    st.markdown('---')
    # BAIXANDO BASE DE DADOS
    df = pd.read_csv('base_de_dados.csv')
    

    # CRIANDO LISTA DO SELECTBOX DAS LIGAS
    ligas_list = list(df['League'].unique())
    
    # COLUNAS PARA SELECIONAR LIGA E TIME
    col1, col2 = st.columns(2)

    # COLUNA 1
    with col1:
        # SELECTBOX DAS LIGAS
        liga = st.selectbox('Escolha a liga', ligas_list)
        
        # FILTRANDO TIMES DE ACORDO COM A LIGA
        times = df[df['League'] == liga].sort_values('Home')
        times = list(times['Home'].unique())

    # COLUNA 2   
    with col2:
        # SELECTBOX DOS TIMES
        time_1 = st.selectbox('Escolha o time da análise', times)

    # FILTRAGEM DOS ÚTIMOS 5 JOGOS DOS TIMES EM CASA E FORA
    df_home_coluna_1 = df[df['Home'] == time_1].tail(5).reset_index(drop=True)
    df_away_coluna_1 = df[df['Away'] == time_1].tail(5).reset_index(drop=True)

    # TRATAMENTO DAS VARIÁVEIS
    df_home_coluna_1['Goals_H_FT'] = df_home_coluna_1['Goals_H_FT'].astype(int) 
    df_home_coluna_1['Goals_A_FT'] = df_home_coluna_1['Goals_A_FT'].astype(int) 
    df_home_coluna_1['Date'] = pd.to_datetime(df_home_coluna_1['Date']).dt.strftime('%d/%m/%Y')

    df_away_coluna_1['Goals_H_FT'] = df_away_coluna_1['Goals_H_FT'].astype(int) 
    df_away_coluna_1['Goals_A_FT'] = df_away_coluna_1['Goals_A_FT'].astype(int) 
    df_away_coluna_1['Date'] = pd.to_datetime(df_away_coluna_1['Date']).dt.strftime('%d/%m/%Y')

    # SUBTITULO
    st.markdown('---')
    st.subheader('Análise dos últimos 5 jogos em casa')

    # CRIANDO VARRÁVEIS PARA APRESENTAR NO ST.MATRICS
    quantidade_de_vitorias = len(df_home_coluna_1[df_home_coluna_1['Result_FT'] == 'H'])
    media_de_pontos = df_home_coluna_1.iloc[-1]['Media_Pontos_H']
    media_de_gols_feitos = df_home_coluna_1.iloc[-1]['Media_Gols_Feitos_Home']
    media_de_gols_sofridos = df_home_coluna_1.iloc[-1]['Media_Gols_Sofridos_Home']
    media_de_05ft = df_home_coluna_1.iloc[-1]['Porc_Over05FT_Home']
    media_de_15ft = df_home_coluna_1.iloc[-1]['Porc_Over15FT_Home']
    media_de_25ft = df_home_coluna_1.iloc[-1]['Porc_Over25FT_Home']
    media_de_btts = df_home_coluna_1.iloc[-1]['Porc_BTTS_Home']

    # CRIANDO 4 COLUNAS
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label='QUANTIDADE DE VITÓRIAS', value=quantidade_de_vitorias)
    
    with col2:
        st.metric(label='MÉDIA DE PONTOS EM CASA', value=media_de_pontos)

    with col3:
        st.metric(label='MÉDIA DE GOLS FEITOS', value=media_de_gols_feitos)

    with col4:
        st.metric(label='MÉDIA DE GOLS SOFRIDOS', value=media_de_gols_sofridos)


    # CRIANDO 4 COLUNAS
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label='OVER 05FT', value=(str(media_de_05ft) + '%'))
    
    with col2:
        st.metric(label='OVER 15FT', value=(str(media_de_15ft) + '%'))

    with col3:
        st.metric(label='OVER 25FT', value=(str(media_de_25ft) + '%'))

    with col4:
        st.metric(label='AMBAS MARCAM', value=(str(media_de_btts) + '%'))
    
    # APRESENTAÇÃO DOS ÚLTIMOS JOGOS
    st.write(df_home_coluna_1[['League', 'Date', 'Home', 'Goals_H_FT', 'Goals_A_FT', 'Away', 'Result_FT']])


    # SUBTITULO
    st.markdown('---')
    st.subheader('Análise dos últimos 5 jogos fora de casa')

    # CRIANDO VARRÁVEIS PARA APRESENTAR NO ST.MATRICS
    quantidade_de_vitorias = len(df_away_coluna_1[df_away_coluna_1['Result_FT'] == 'A'])
    media_de_pontos = df_away_coluna_1.iloc[-1]['Media_Pontos_A']
    media_de_gols_feitos = df_away_coluna_1.iloc[-1]['Media_Gols_Feitos_Away']
    media_de_gols_sofridos = df_away_coluna_1.iloc[-1]['Media_Gols_Sofridos_Away']
    media_de_05ft = df_away_coluna_1.iloc[-1]['Porc_Over05FT_Away']
    media_de_15ft = df_away_coluna_1.iloc[-1]['Porc_Over15FT_Away']
    media_de_25ft = df_away_coluna_1.iloc[-1]['Porc_Over25FT_Away']
    media_de_btts = df_away_coluna_1.iloc[-1]['Porc_BTTS_Away']

    # CRIANDO 4 COLUNAS
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label='QUANTIDADE DE VITÓRIAS', value=quantidade_de_vitorias)
    
    with col2:
        st.metric(label='MÉDIA DE PONTOS FORA', value=media_de_pontos)

    with col3:
        st.metric(label='MÉDIA DE GOLS FEITOS', value=media_de_gols_feitos)

    with col4:
        st.metric(label='MÉDIA DE GOLS FORA', value=media_de_gols_sofridos)


    # CRIANDO 4 COLUNAS
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label='OVER 05FT', value=(str(media_de_05ft) + '%'))
    
    with col2:
        st.metric(label='OVER 15FT', value=(str(media_de_15ft) + '%'))

    with col3:
        st.metric(label='OVER 25FT', value=(str(media_de_25ft) + '%'))

    with col4:
        st.metric(label='AMBAS MARCAM', value=(str(media_de_btts) + '%'))
    
    # APRESENTAÇÃO DOS ÚLTIMOS JOGOS
    st.write(df_away_coluna_1[['League', 'Date', 'Home', 'Goals_H_FT', 'Goals_A_FT', 'Away', 'Result_FT']])

    
def financas():
    with st.expander('ESCOLHA UMA DAS OPÇÕES PARA ESCOLHER SUA ANÁLISE', expanded=True):
        st.subheader('Escolha uma das opções para continuar')
        opcoes = ['Analisar Fundamentos de Ações', 'Análise de setor', 'Backtest']
        escolha = st.radio('Escolha uma opção', options=opcoes)


    if escolha == 'Analisar Fundamentos de Ações':
    
        st.title('Informações Fundamentalistas das ações e histórico de preços de 1 ano')

        tickers_IBOV = ['ABEV3', 'ALPA4', 'AMER3', 'ASAI3', 'AZUL4', 'B3SA3', 'BBAS3', 'BBDC3', 'BBDC4', 'BBSE3', 'BEEF3', 
                'BPAC11', 'BPAN4', 'BRAP4', 'BRFS3', 'BRKM5', 'BRML3', 'CASH3', 'CCRO3', 'CIEL3', 'CMIG4', 'CMIN3', 
                'COGN3', 'CPFE3', 'CPLE6', 'CRFB3', 'CSAN3', 'CSNA3', 'CVCB3', 'CYRE3', 'DXCO3', 'ECOR3', 'EGIE3', 
                'ELET3', 'ELET6', 'EMBR3', 'ENBR3', 'ENEV3', 'ENGI11', 'EQTL3', 'EZTC3', 'FLRY3', 'GGBR4', 'GOAU4', 
                'GOLL4', 'HAPV3', 'HYPE3', 'IGTI11', 'IRBR3', 'ITSA4', 'ITUB4', 'JBSS3', 'JHSF3', 'KLBN11', 
                'LREN3', 'LWSA3', 'MGLU3', 'MRFG3', 'MRVE3', 'MULT3', 'NTCO3', 'PCAR3', 'PETR3', 'PETR4', 'PETZ3', 
                'POSI3', 'PRIO3', 'QUAL3', 'RADL3', 'RAIL3', 'RDOR3', 'RENT3', 'RRRP3', 'SANB11', 'SBSP3', 'SLCE3', 
                'SOMA3', 'SULA11', 'SUZB3', 'TAEE11', 'TIMS3', 'TOTS3', 'UGPA3', 'USIM5', 'VALE3', 'VBBR3', 'VIIA3', 
                'VIVT3', 'WEGE3', 'YDUQ3', 'LEVE3', 'MTRE3', 'NEO3', 'RANI3', 'CXSE']

        with st.expander('Ativo 1', expanded=True):
            papel1 = st.selectbox('Selecione o Papel', tickers_IBOV)
            info_papel1 = fd.get_detalhes_papel(papel1)
            st.write('**Empresa:**', info_papel1['Empresa'][0])
            st.write('**Setor:**', info_papel1['Setor'][0])
            st.write('**Subsetor:**', info_papel1['Subsetor'][0])
            st.markdown('---')
            col1, col2 = st.columns(2)
            with col1:
                try:
                    st.write('- **Valor de Mercado:**',f"R$ {info_papel1['Valor_de_mercado'][0]:,.2f}")
                except:
                    st.write('- **Valor de Mercado:**', "Sem informação")

                try:
                    st.write('- **Patrimônio Líquido:**', f"R$ {float(info_papel1['Patrim_Liq'][0]):,.2f}")
                except:
                    st.write('- **Patrimônio Líquido:**', "Sem informação")

                try:
                    st.write('- **Receita Liq. 12m:**', f"R$ {float(info_papel1['Receita_Liquida_12m'][0]):,.2f}")
                except:
                    st.write('- **Receita Liq. 12m:**', "Sem informação")

                try:
                    st.write('- **Dívida Bruta:**', f"R$ {float(info_papel1['Div_Bruta'][0]):,.2f}")
                except:
                    st.write('- **Dívida Bruta:**', "Sem informação")
                
                try:
                    st.write('- **Dívida Líquida:**', f"R$ {float(info_papel1['Div_Liquida'][0]):,.2f}")
                except:
                    st.write('- **Dívida Líquida:**', "Sem informação")
                
                try:
                    st.write('- **P/L:**', f"{float(info_papel1['PL'][0])/100}")
                except:
                    st.write('- **P/L:**', "Sem informação")
                
                try:
                    st.write('- **P/VP:**', f"{float(info_papel1['PVP'][0])/100}")
                except:
                    st.write('- **P/VP:**', "Sem informação")

            with col2:
                try:
                    st.write('- **ROE:**',f"{info_papel1['ROE'][0]}")
                except:
                    st.write('- **ROE:**', "Sem informação")
                
                try:
                    st.write('- **GIRO ATIVOS:**',f"{(float(info_papel1['Giro_Ativos'][0])/100)}")
                except:
                    st.write('- **GIRO ATIVOS:**', "Sem informação")

                try:
                    st.write('- **EBIT 3 MESES:**',f"R$ {float(info_papel1['EBIT_3m'][0]):,.2f}")
                except:
                    st.write('- **EBIT 3 MESES:**', "Sem informação")
                
                try:
                    st.write('- **EBIT 12 MESES:**',f"R$ {float(info_papel1['EBIT_12m'][0]):,.2f}")
                except:
                    st.write('- **EBIT 12 MESES:**', "Sem informação")
                
                try:
                    st.write('- **MARGEM LÍQUIDA:**',f"{(info_papel1['Marg_Liquida'][0])}")
                except:
                    st.write('- **MARGEM LÍQUIDA:**', "Sem informação")

                try:
                    st.write('- **Dividend Yield:**', f"{info_papel1['Div_Yield'][0]}")
                except:
                    st.write('- **Dividend Yield:**', "Sem informação")

                try:
                    st.write('- **CRESCIMENTOS 5 ANOS:**',f"{info_papel1['Cres_Rec_5a'][0]}%")
                except:
                    st.write('- **CRESCIMENTOS 5 ANOS:**', "Sem informação")
        st.markdown('---')
        st.subheader(f'Análise da cotação histórica {papel1}')
        acao = yf.download((papel1 + '.SA'), period='1y')
        tamanho = len(acao) - 1
        col1,col2,col3 = st.columns(3)
    
        with col1:
            st.metric(label='**COTAÇÃO ATUAL**', value=f'R$ {(round(acao.iloc[-1,-2], 2)):,.2f}')
        with col2:
            st.metric(label='**MAIOR COTAÇÃO**', value=f'R$ {(round(acao.iloc[:,-2].max(), 2)):,.2f}')
        with col3:
            st.metric(label='**MENOR COTAÇÃO**', value=f'R$ {(round(acao.iloc[:,-2].min(), 2)):,.2f}')

        fig = go.Figure(data=[go.Candlestick(x=acao.index,
                open=acao['Open'],
                high=acao['High'],
                low=acao['Low'],
                close=acao['Close'])])
        st.plotly_chart(fig, theme=None, use_container_width=True)

    if escolha == 'Análise de setor':
        tickers_IBOV = ['ABEV3', 'ALPA4', 'AMER3', 'ASAI3', 'AZUL4', 'B3SA3', 'BBAS3', 'BBDC3', 'BBDC4', 'BBSE3', 'BEEF3', 
                'BPAC11', 'BPAN4', 'BRAP4', 'BRFS3', 'BRKM5', 'BRML3', 'CASH3', 'CCRO3', 'CIEL3', 'CMIG4', 'CMIN3', 
                'COGN3', 'CPFE3', 'CPLE6', 'CRFB3', 'CSAN3', 'CSNA3', 'CVCB3', 'CYRE3', 'DXCO3', 'ECOR3', 'EGIE3', 
                'ELET3', 'ELET6', 'EMBR3', 'ENBR3', 'ENEV3', 'ENGI11', 'EQTL3', 'EZTC3', 'FLRY3', 'GGBR4', 'GOAU4', 
                'GOLL4', 'HAPV3', 'HYPE3', 'IGTI11', 'IRBR3', 'ITSA4', 'ITUB4', 'JBSS3', 'JHSF3', 'KLBN11', 
                'LREN3', 'LWSA3', 'MGLU3', 'MRFG3', 'MRVE3', 'MULT3', 'NTCO3', 'PCAR3', 'PETR3', 'PETR4', 'PETZ3', 
                'POSI3', 'PRIO3', 'QUAL3', 'RADL3', 'RAIL3', 'RDOR3', 'RENT3', 'RRRP3', 'SANB11', 'SBSP3', 'SLCE3', 
                'SOMA3', 'SULA11', 'SUZB3', 'TAEE11', 'TIMS3', 'TOTS3', 'UGPA3', 'USIM5', 'VALE3', 'VBBR3', 'VIIA3', 
                'VIVT3', 'WEGE3', 'YDUQ3', 'LEVE3', 'MTRE3', 'NEO3', 'RANI3', 'CXSE']


        st.title('ANÁLISE DAS AÇÕES POR SETOR')
        tabela_ref = pd.read_excel('tabela_de_acoes_ref.xlsx')
        tabela = pd.DataFrame()
        for i in tickers_IBOV:
            intermediario = tabela_ref[tabela_ref['Ticker'] == i]
            tabela = pd.concat([tabela, intermediario])
        tabela_ref = tabela.reset_index(drop=True)
        # ESCOLHENDO O SETOR DE ANÁLISE PARA GERAR OS GRÁFICOS
        setores = tabela_ref.Setor.unique()
        valor = st.selectbox('INFORME O SETOR QUE DESEJA ANALISAR', setores)
        
        setor = list(tabela_ref[tabela_ref['Setor'] == valor]['Ticker'])
        analise_setor = pd.DataFrame()
        for i in setor:
            df = fd.get_resultado_raw()
            df = df[df.index == i]
            analise_setor = pd.concat([analise_setor, df])

        analise_setor.dropna(inplace=True)
        fig1 = make_subplots(rows=1,
                    cols=2,
                    subplot_titles=('P/VP', 'P/L'),
                    shared_xaxes=False)
        fig1.add_trace(go.Bar(x=analise_setor.index, y=analise_setor['P/VP']), row=1, col=1)
        fig1.add_trace(go.Bar(x=analise_setor.index, y=analise_setor['P/L']), row=1, col=2)
        fig1.update_layout(title_text=f'<b>Avaliação Fundamentalista do setor: {valor}<b>', 
                    template='plotly_dark',#template pré-definido da plotly
                    showlegend=False, #esconder ou mostrar legenda
                    ) #largura
        st.plotly_chart(fig1, theme=None, use_container_width=True)

        fig2 = make_subplots(rows=1,
                    cols=2,
                    subplot_titles=('Div.Yield', 'P/Ativo'),
                    shared_xaxes=False)
        fig2.add_trace(go.Bar(x=analise_setor.index, y=analise_setor.loc[:, 'Div.Yield']), row=1, col=1)
        fig2.add_trace(go.Bar(x=analise_setor.index, y=analise_setor.loc[:, 'P/Ativo']), row=1, col=2)
        fig2.update_layout(title_text=f'<b>Avaliação Fundamentalista do setor: {valor}<b>', 
                    template='plotly_dark',#template pré-definido da plotly
                    showlegend=False, #esconder ou mostrar legenda
                    ) #largura
        st.plotly_chart(fig2, theme=None, use_container_width=True)

        fig3 = make_subplots(rows=1,
                    cols=2,
                    subplot_titles=('Mrg Ebit', 'Mrg. Líq.'),
                    shared_xaxes=False)
        fig3.add_trace(go.Bar(x=analise_setor.index, y=analise_setor.loc[:, 'Mrg Ebit']), row=1, col=1)
        fig3.add_trace(go.Bar(x=analise_setor.index, y=analise_setor.loc[:, 'Mrg. Líq.']), row=1, col=2)
        fig3.update_layout(title_text=f'<b>Avaliação Fundamentalista do setor: {valor}<b>', 
                    template='plotly_dark',#template pré-definido da plotly
                    showlegend=False, #esconder ou mostrar legenda
                    ) #largura
        st.plotly_chart(fig3, theme=None, use_container_width=True)

        fig4 = make_subplots(rows=1,
                    cols=2,
                    subplot_titles=('Patrim. Líq', 'Dív.Brut/ Patrim.'),
                    shared_xaxes=False)
        fig4.add_trace(go.Bar(x=analise_setor.index, y=analise_setor.loc[:, 'Patrim. Líq']), row=1, col=1)
        fig4.add_trace(go.Bar(x=analise_setor.index, y=analise_setor.loc[:, 'Dív.Brut/ Patrim.']), row=1, col=2)
        fig4.update_layout(title_text=f'<b>Avaliação Fundamentalista do setor: {valor}<b>', 
                    template='plotly_dark',#template pré-definido da plotly
                    showlegend=False, #esconder ou mostrar legenda
                    ) #largura
        st.plotly_chart(fig4, theme=None, use_container_width=True)
        
        fig5 = make_subplots(rows=1,
                    cols=2,
                    subplot_titles=('ROE', 'P/EBIT'),
                    shared_xaxes=False)
        fig5.add_trace(go.Bar(x=analise_setor.index, y=analise_setor.loc[:, 'ROE']), row=1, col=1)
        fig5.add_trace(go.Bar(x=analise_setor.index, y=analise_setor.loc[:, 'P/EBIT']), row=1, col=2)
        fig5.update_layout(title_text=f'<b>Avaliação Fundamentalista do setor: {valor}<b>', 
                    template='plotly_dark',#template pré-definido da plotly
                    showlegend=False, #esconder ou mostrar legenda
                    ) #largura
        st.plotly_chart(fig5, theme=None, use_container_width=True)
    
    if escolha == 'Backtest':
        st.subheader('Modelo de otimização de portifólio HRP(Hierarchical Risk Parity)')
        st.markdown('O Hierarchical Risk Parity (HRP) é um algoritmo de otimização de portfólios desenvolvido por Marcos Lopez de Prado. Esse otimizador combina teoria de grafos e machine learning para construir uma carteira diversificada com soluções estáveis.')
        st.markdown('---')

        tickers_IBOV = ['ABEV3', 'ALPA4', 'AMER3', 'ASAI3', 'AZUL4', 'B3SA3', 'BBAS3', 'BBDC3', 'BBDC4', 'BBSE3', 'BEEF3', 
                'BPAC11', 'BPAN4', 'BRAP4', 'BRFS3', 'BRKM5', 'BRML3', 'CASH3', 'CCRO3', 'CIEL3', 'CMIG4', 'CMIN3', 
                'COGN3', 'CPFE3', 'CPLE6', 'CRFB3', 'CSAN3', 'CSNA3', 'CVCB3', 'CYRE3', 'DXCO3', 'ECOR3', 'EGIE3', 
                'ELET3', 'ELET6', 'EMBR3', 'ENBR3', 'ENEV3', 'ENGI11', 'EQTL3', 'EZTC3', 'FLRY3', 'GGBR4', 'GOAU4', 
                'GOLL4', 'HAPV3', 'HYPE3', 'IGTI11', 'IRBR3', 'ITSA4', 'ITUB4', 'JBSS3', 'JHSF3', 'KLBN11', 
                'LREN3', 'LWSA3', 'MGLU3', 'MRFG3', 'MRVE3', 'MULT3', 'NTCO3', 'PCAR3', 'PETR3', 'PETR4', 'PETZ3', 
                'POSI3', 'PRIO3', 'QUAL3', 'RADL3', 'RAIL3', 'RDOR3', 'RENT3', 'RRRP3', 'SANB11', 'SBSP3', 'SLCE3', 
                'SOMA3', 'SULA11', 'SUZB3', 'TAEE11', 'TIMS3', 'TOTS3', 'UGPA3', 'USIM5', 'VALE3', 'VBBR3', 'VIIA3', 
                'VIVT3', 'WEGE3', 'YDUQ3', 'LEVE3', 'MTRE3', 'NEO3', 'RANI3', 'CXSE']
        tickers_IBOV = [ticker + '.SA' for ticker in tickers_IBOV]

        with st.form(key='form2'):
            st.subheader('ESCOLHA AS AÇÕES PARA CONTINUAR')
            opcoes = ['Análise de uma ação', 'Análise de setor', 'Backtest']
            ativos = st.multiselect('Escolha uma opção', options=tickers_IBOV)
            valor = st.number_input(label='INFORME O VALOR DE INVESTIMENTO NO PORTIFÓLIO')
            otimizacao = st.form_submit_button('Otimização')
        st.markdown('---')
        
        if otimizacao and len(ativos) > 0:
            with st.spinner('FAZENDO O BACKTEST'):
                # BACKTEST
                acoes = baixar_cotacoes_acoes(ativos)
                matriz_covarianca, colunas_seriation = matrix_seriation(acoes)
                pesos = calcula_pesos_hrp(matriz_covarianca, colunas_seriation)
                fig, vol_ano, drawdown, sharpe_ratio, retorno_da_carteira, dividendo, qtd_de_acoes = back_testing(ativos, pesos, valor)

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric(label='RETORNO DO PORTIFÓLIO', value=f'{round((retorno_da_carteira * 100),2)}%')
            with col2:
                st.metric(label='DIVIDENDOS RECEBIDOS', value=f'R$ {round((dividendo), 2):,.2f}')
            with col3:
                st.metric(label='VOLATILIDADE', value=f'{round((vol_ano[0][0]),2)}')
            with col4:
                st.metric(label='MÁXIMO DRAWDOWN', value=f'{round((drawdown), 2)}')
            with col5:
                st.metric(label='SHARPE RATIO', value=f'{round((sharpe_ratio[0][0]), 2)}')
            
            st.plotly_chart(fig, theme=None, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('PESOS DAS AÇÕES NO BACKTES')
                for ativo in ativos:
                    st.markdown(f'**{ativo}**: \n- Peso na carteira: {round((pesos[ativo]*100), 2)}% \n- Quantidade de ações: {int(qtd_de_acoes[ativo])}')

            with col2:
                st.markdown('NOVA OTIMIZAÇÃO DE PORTIFÓLIO')
                with st.spinner('GERANDO UM NOVO BACKTEST'):
                # BACKTEST
                    acoes = yf.download(ativos, period='2y')['Adj Close']
                    acoes = acoes.pct_change().dropna()
                    matriz_covarianca, colunas_seriation = matrix_seriation(acoes)
                    pesos = calcula_pesos_hrp(matriz_covarianca, colunas_seriation)
                    #fig, vol_ano, drawdown, sharpe_ratio, retorno_da_carteira = back_testing(ativos, pesos)
                    qtd_de_acoes = quantidade_de_acoes_para_comprar(ativos, valor, pesos)

                for ativo in ativos:
                    st.markdown(f'**{ativo}**: \n- Peso na carteira: {round((pesos[ativo]*100), 2)}% \n- Quantidade de ações: {int(qtd_de_acoes[ativo])}')

# Função principal
def main_projeto():
    st.set_page_config(
        page_title="Página - LeoFMedeiros",
        page_icon="🧊",
        layout="wide",      
    )
    st.sidebar.image('capa-datascience.png', width=300)
    st.sidebar.title('Página de Projetos @LeoFMedeiros')
    st.sidebar.markdown('---')
    
    paginas = ['Apresentação', 'Futebol', 'Mercado Financeiro']
    escolha = st.sidebar.radio('Escolha a Página', paginas)

    if escolha == 'Apresentação':
        apresentacao()

    if escolha == 'Futebol':
        futebol()

    if escolha == 'Mercado Financeiro':
        financas()

main_projeto()
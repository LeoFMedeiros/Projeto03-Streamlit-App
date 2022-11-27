import streamlit as st
import pandas as pd


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

    











# Função principal
def main_projeto():
    st.sidebar.image('capa-datascience.png', width=300)
    st.sidebar.title('Página de Projetos @LeoFMedeiros')
    st.sidebar.markdown('---')
    
    paginas = ['Apresentação', 'Futebol']
    escolha = st.sidebar.radio('Escolha a Página', paginas)

    if escolha == 'Apresentação':
        apresentacao()

    if escolha == 'Futebol':
        futebol()

main_projeto()
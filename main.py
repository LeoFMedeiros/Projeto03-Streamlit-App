import streamlit as st

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



def financas():
    st.title('EM CONSTRUÇÃO')

def futebol():
    st.title('EM CONSTRUÇÃO')

# Função principal
def main_projeto():
    st.sidebar.image('capa-datascience.png', width=300)
    st.sidebar.title('Página de Projetos @LeoFMedeiros')
    st.sidebar.markdown('---')
    
    paginas = ['Apresentação', 'Finanças', 'Futebol']
    escolha = st.sidebar.radio('Escolha a Página', paginas)

    if escolha == 'Apresentação':
        apresentacao()
    if escolha == 'Finanças':
        financas()
    if escolha == 'Futebol':
        futebol()

main_projeto()
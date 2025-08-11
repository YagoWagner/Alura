import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique()) # Ordena os anos disponíveis
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis) # o st.sidebar.multiselect cria uma caixa de seleção múltipla, com os anos disponíveis, e seleciona todos por padrão.

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique()) # Ordena as senioridades disponíveis
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis) # o st.sidebar.multiselect cria uma caixa de seleção múltipla, com as senioridades disponíveis, e seleciona todos por padrão.

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis) # o st.sidebar.multiselect cria uma caixa de seleção múltipla, com os tipos de contrato disponíveis, e seleciona todos por padrão.

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis) # o st.sidebar.multiselect cria uma caixa de seleção múltipla, com os tamanhos de empresa disponíveis, e seleciona todos por padrão.


# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
] 
# O df_filtrado agora contém apenas os dados que correspondem aos filtros selecionados pelo usuário.


# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.") # o st.markdown permite adicionar texto formatado, como títulos e descrições.


# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)") # o st.subheader cria um subtítulo para a seção de métricas gerais.


if not df_filtrado.empty: # Verifica se o DataFrame filtrado não está vazio antes de calcular as métricas.
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4) # esses cols criam quatro colunas para exibir as métricas lado a lado. E o st.columns permite dividir a página em colunas.
col1.metric("Salário médio", f"${salario_medio:,.0f}") # o col1.metric exibe uma métrica com um título e um valor formatado. 
col2.metric("Salário máximo", f"${salario_maximo:,.0f}") # o col2.metric exibe uma métrica com um título e um valor formatado.
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2) # o col_graf1 e col_graf2 criam duas colunas para exibir os gráficos lado a lado.

with col_graf1: # o with é usado para agrupar o código que será executado dentro de uma coluna específica.
    # Gráfico de barras para os 10 cargos com maior salário médio
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index() # Agrupa os dados por cargo, calcula a média salarial e seleciona os 10 maiores salários médios, ordenando-os em ordem crescente.
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h', # Define a orientação horizontal do gráfico de barras
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''} # Labels para os eixos do gráfico
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'}) # Atualiza o layout do gráfico, centralizando o título e ordenando os cargos pelo salário médio de forma ascendente.
        st.plotly_chart(grafico_cargos, use_container_width=True) # o st.plotly_chart exibe o gráfico Plotly na aplicação Streamlit.
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)


# Libraries
from haversine import haversine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static


st.set_page_config( page_title='Visão Empresa', layout='wide' )
#============================================================
#Funções
#============================================================
def country_maps(df1):
    df_aux = ( df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                  .groupby(['City', 'Road_traffic_density'])
                  .median()
                  .reset_index() )
    # desenhando no mapa
    map = folium.Map()
    # incluir marcação no mapa com a localização dos deliverys
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static( map, width=1024, height=600)

    return None

def order_share_by_week(df1):
    # Qt de pedidos por semana / Entregadores únicos por semana
    df_aux01 = ( df1.loc[:,['ID', 'week_of_year']]
                    .groupby('week_of_year')
                    .count()
                    .reset_index() )
    df_aux02 = ( df1.loc[:,['Delivery_person_ID', 'week_of_year']]
                    .groupby('week_of_year')
                    .nunique()
                    .reset_index() )

    # juntar dois dataframe
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    # percentual de pedidos por entregador
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # desenhando o grafico de linhas
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def order_by_week(df1):
    # criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U')
    #Selecionando os dados no dataframe
    df_aux = ( df1.loc[:, ['ID', 'week_of_year']]
                  .groupby(['week_of_year'])
                  .count()
                  .reset_index() )
    # Desenhar graficos de linhas
    fig = px.line( df_aux, x='week_of_year', y='ID')

    return fig

def traffic_order_city(df1):
    # Contagem
    df_aux = ( df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                  .groupby(['City', 'Road_traffic_density'])
                  .count()
                  .reset_index() )
    # desenhar grafico de bolhas
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def traffic_order_share(df1):
    # contagem
    df_aux = ( df1.loc[:, ['ID', 'Road_traffic_density']]
                  .groupby(['Road_traffic_density'])
                  .count()
                  .reset_index() )
    # criação da coluna com o percentual da distribuição do pedido por tipo de tráfego
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    # desenhando gráfico de pizza
    fig = px.pie(df_aux, names='Road_traffic_density', values='entregas_perc')
    
    return fig

def order_metric(df1):
    # seleção das linhas
    df_aux = ( df1.loc[:, ['ID', 'Order_Date']]
                  .groupby('Order_Date')
                  .count()
                  .reset_index() )
    fig = px.bar(df_aux, x= 'Order_Date', y= 'ID')

    return fig

def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataFrame 
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texo
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
        
        Input: Dataframe
        Output: Dataframe """
    
    # convertendo a coluna age  de texto para numero inteiro (int)
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :]

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # convertendo a coluna Ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # convertendo a coluna Order_Date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # convertendo a coluna multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :]

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # remover espaços sem usar o laço for
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    #Retirando os valores NaN das colunas City e Road_traffic_density
    df1 = df1.loc[df1['City'] != 'NaN']
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN']
    df1 = df1.loc[df1['Festival'] != 'NaN']

    df1 = df1.reset_index( drop = True)

    # Limpando a coluna de 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1



##===========================================================Inicio da Estrutura lógica do código============================================================
#============================================================
# Import dataset
#============================================================
df = pd.read_csv( 'dataset/train.csv' )

#============================================================
# Limpando os dados
#============================================================
df1 = clean_code (df)


#============================================================
# Barra Lateral - Streamlit
#============================================================

st.header('Marketplace - Visão Cliente', divider='blue')

#image_path = 'C:\\Users\\Tiago\\repos\\ftc_programacao_python\\meta.png' # por se tratar de windows tenho que usar barra dupla
image = Image.open( 'meta.png' )

st.sidebar.image(image, width=120)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""")
st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?', 
    value=pd.datetime( 2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown( """---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown( """---""")

st.sidebar.markdown( '### Desenvolvido by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#============================================================
# Layout do Streamlit
#============================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        st.markdown("<h1 style='text-align: center;'>  Order by Day</h1>", unsafe_allow_html=True)
        fig = order_metric(df1)
        st.plotly_chart (fig, use_container_width=True)
      
    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            #st.markdown("<h1 style='text-align: center;'>  Coluna 1</h1>", unsafe_allow_html=True)
            st.header('Traffic Order Share')
            fig = traffic_order_share (df1)
            st.plotly_chart (fig, use_container_width=True)         

        with col2:
            #st.markdown("<h1 style='text-align: center;'>  Coluna 2</h1>", unsafe_allow_html=True)
            st.header('Traffic Order City')
            fig = traffic_order_city (df1)
            st.plotly_chart (fig, use_container_width=True)      

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week (df1)
        st.plotly_chart (fig, use_container_width=True)     
          
    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week (df1)
        st.plotly_chart (fig, use_conteiner_width=True)        

with tab3:
    st.markdown('# Country Maps')
    country_maps (df1)    

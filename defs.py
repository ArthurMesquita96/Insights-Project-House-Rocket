import numpy as np
import geopandas
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import plotly.express as px


@st.cache(allow_output_mutation=True)
def getdata(path):
    data = pd.read_csv(path)
    return data


@st.cache(allow_output_mutation=True)
def get_geofile(url):
    geofile = geopandas.read_file(url)

    return geofile


def set_feature(data):
    # add new features
    data['price_m2'] = data['price'] / data['sqft_lot']

    # Convertendo para datimetime
    # data['date'] = pd.to_datetime(data['date'], format="%Y-%m-%d")

    # Convertendo pés quadrados para metros quadrados (m²)
    data['sqft_living'] = data['sqft_living'] * 0.092903
    data['sqft_lot'] = data['sqft_lot'] * 0.092903
    data['sqft_living15'] = data['sqft_living15'] * 0.092903
    data['sqft_lot15'] = data['sqft_lot15'] * 0.092903

    # Adicionar colunas de dia, semana, mês e ano

    data['year'] = 'NA'
    data['week_of_year'] = 'NA'
    data['month'] = 'NA'
    data['day'] = 'NA'

    data['year'] = data['date'].dt.year
    data['week_of_year'] = data['date'].dt.isocalendar().week
    data['month'] = data['date'].dt.month
    data['day'] = data['date'].dt.day

    # Adicionar coluna com a estação do ano
    data['seasons'] = data['date'].apply(lambda x: 'Spring' if (x.day_of_year > 80) & (x.day_of_year <= 173) else
                                                    'Summer' if (x.day_of_year > 173) & (x.day_of_year <= 267) else
                                                    'Fall' if (x.day_of_year > 267) & (x.day_of_year <= 356) else
                                                    'Winter')
    return data

def overview_data(data, geofile):
    # ==================
    # Data Overview
    # ==================
    st.header('Dataset Sample')
    f_attributes = st.sidebar.multiselect('Enter columns', data.columns)
    f_zipcode = st.sidebar.multiselect('Enter zipcode', data['zipcode'].unique())
    df = data.copy()

    if (f_zipcode != []) & (f_attributes != []):
        data = data.loc[data['zipcode'].isin(f_zipcode), f_attributes]
    elif (f_zipcode != []) & (f_attributes == []):
        data = data.loc[data['zipcode'].isin(f_zipcode), :]
    elif (f_zipcode == []) & (f_attributes != []):
        data = data.loc[:, f_attributes]
    else:
        data = data.copy()

    st.dataframe(data, height=200)

    # ==============================
    # Average metrics
    # ==============================

    c1, c2 = st.columns((1, 1))

    df1 = df[['id', 'zipcode']].groupby('zipcode').count().reset_index()
    df2 = df[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df3 = df[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
    df4 = df[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()

    # merge
    m1 = pd.merge(df1, df2, on='zipcode', how='inner')
    m2 = pd.merge(m1, df3, on='zipcode', how='inner')
    df_metrics = pd.merge(m2, df4, on='zipcode', how='inner')

    df_metrics.columns = ['Zipcode', 'Total Houses', 'Price', 'SQRT Living', 'Price_m2']

    c1.header('Average Prices')
    c1.dataframe(df_metrics, height=500)

    # =================================
    # Gráfico 2 (direita)
    # =================================

    # Region Price Map
    c2.header('Price Density')
    df = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df.columns = ['ZIP', 'PRICE']
    geofile = geofile[geofile['ZIP'].isin(geofile['ZIP'].tolist())]
    region_price_map = folium.Map(location=[data['lat'].mean(),
                                            data['long'].mean()],
                                  default_zoom_start=15)

    region_price_map.choropleth(data=df,
                                geo_data=geofile,
                                columns=['ZIP', 'PRICE'],
                                key_on='feature.properties.ZIP',
                                fill_color='YlOrRd',
                                fill_opacity=0.7,
                                line_opacity=0.2,
                                legend_name='AVG PRICE')
    with c2:
        folium_static(region_price_map)

    # ==================================
    # Descriptive Analysis
    # ==================================

    num_attributes = data.select_dtypes(include=['int64', 'float64'])

    media = pd.DataFrame(num_attributes.apply(np.mean))
    mediana = pd.DataFrame(num_attributes.apply(np.median))
    std = pd.DataFrame(num_attributes.apply(np.std))
    max_ = pd.DataFrame(num_attributes.apply(np.max))
    min_ = pd.DataFrame(num_attributes.apply(np.min))

    df_descriptive = pd.concat([max_, min_, media, mediana, std], axis=1).reset_index()
    df_descriptive.columns = ['attributes', 'max', 'min', 'media', 'median', 'std']

    st.header('Descriptive Analysis')
    st.dataframe(df_descriptive, height=400)

    return None


def portfolio_density(data, _):

    st.header('Region Overview')

    st.caption('''
        Displays the total number of houses available for purchase by region on the map
        ''')

    # =================================
    # Gráfico 1 (esquerda)
    # =================================

    # Base Map - Folium
    density_map = folium.Map(location=[data['lat'].mean(),
                                       data['long'].mean()],
                             default_zoom_start=15)

    marker_cluster = MarkerCluster().add_to(density_map)
    for name, row in data.iterrows():
        folium.Marker([row['lat'], row['long']],
                      popup='Sold R${0} on: {1}. Features: {2} sqft, {3} bedrooms, {4} bathrooms, year built: {5}'.format(
                          row['price'],
                          row['date'],
                          row['sqft_living'],
                          row['bedrooms'],
                          row['bathrooms'],
                          row['yr_built'])).add_to(marker_cluster)
    folium_static(density_map)
    return None


def zipcode_price_density(data, geofile):
    # =================================
    # Gráfico de Pre~ço por Região
    # =================================

    # Region Price Map
    st.header('Price Density')
    st.caption('''
                Displays the average property price by region        
                ''')

    df = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    df.columns = ['ZIP', 'PRICE']
    geofile = geofile[geofile['ZIP'].isin(geofile['ZIP'].tolist())]
    region_price_map = folium.Map(location=[data['lat'].mean(),
                                            data['long'].mean()],
                                  default_zoom_start=15)

    region_price_map.choropleth(data=df,
                                geo_data=geofile,
                                columns=['ZIP', 'PRICE'],
                                key_on='feature.properties.ZIP',
                                fill_color='YlOrRd',
                                fill_opacity=0.7,
                                line_opacity=0.2,
                                legend_name='AVG PRICE')

    folium_static(region_price_map)

    return None


def price_houses(data):
    if st.checkbox('Click here to edit graph'):
        c1, c2 = st.columns(2)
        choose1 = c1.selectbox("Dot Size", ('price', 'bedrooms', 'bathrooms', 'sqft_living',
                                        'sqft_lot', 'floors', 'waterfront', 'view', 'condition', 'grade',
                                        'sqft_above', 'sqft_basement', 'yr_built', 'yr_renovated'))
        choose2 = c2.selectbox("Dot Color", ('price', 'sqft_living',
                                         'sqft_lot', 'floors', 'waterfront', 'view', 'condition', 'grade',
                                         'sqft_above', 'sqft_basement', 'yr_built', 'yr_renovated'))
        houses_map(data, '', choose1, choose2, ' ', 'Total of houses', len(data))
    else:
        st.header("Houses Price")
        houses_map(data, "", 'price', 'price', 'Display the price of each house as a dot. The lighter colors represents more expensive houses', 'Total of houses', len(data))

    return None

def houses_map(data,header,size,color,comment,metric_title,metric):

    if header != '':
        st.subheader(header)
    if comment != '':
        st.caption(comment)
    st.metric(label=metric_title, value=metric)

    houses = data.copy()

    fig = px.scatter_mapbox(houses,
                            lat='lat',
                            lon='long',
                            color=color,
                            size=size,
                            color_continuous_scale="Viridis",
                            size_max=15,
                            zoom=10)

    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(height=600, margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig)

    return None


def comercial_distribution(data):
    # ================================================
    # Distribuição dos imóveis por categorias comerciais
    # ================================================

    import plotly.express as px
    from datetime import datetime

    st.sidebar.title('Comercial Options')
    st.title('Comercial Attributes')

    # ------- Average Price per Year
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
    min_year_built = int(data['yr_built'].min())
    max_year_built = int(data['yr_built'].max())

    st.sidebar.subheader('Select Max Year Built')
    f_year_built = st.sidebar.slider('Year Built', min_year_built, max_year_built, max_year_built)
    st.header('Average Price per Year built')

    df = data[data['yr_built'] < f_year_built]
    df = df[['yr_built', 'price']].groupby('yr_built').mean().reset_index()

    import plotly.io as pio
    pio.templates.default = 'plotly_dark'

    fig = px.line(df, x='yr_built', y='price', template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    # ------ Average Price per Day

    st.header('Average Price per Day')
    st.sidebar.subheader('Select Max Date')

    min_date = datetime.strptime(data['date'].min(), '%Y-%m-%d')
    max_date = datetime.strptime(data['date'].max(), '%Y-%m-%d')
    f_date = st.sidebar.slider('Date', min_date, max_date, max_date)

    data['date'] = pd.to_datetime(data['date'])
    df = data[data['date'] < f_date]
    df = df[['date', 'price']].groupby('date').mean().reset_index()

    fig = px.line(df, x='date', y='price')
    st.plotly_chart(fig, use_container_width=True)

    # ----- Histpgrama
    st.header('Price distribution')
    st.sidebar.subheader('Select Max Price')
    min_ = int(data['price'].min())
    max_ = int(data['price'].max())

    f_ = st.sidebar.slider('Price', min_, max_, max_)
    df = data[data['price'] < f_]

    fig = px.histogram(df, x='price', nbins=50)
    st.plotly_chart(fig, use_container_width=True)


def attributes_distribution(data):
    st.sidebar.title('Attributes Options')
    st.title('Overview of House Attributes')

    c1, c2 = st.columns(2)

    import plotly.io as pio
    pio.templates.default = 'plotly_dark'

    c1.subheader('Bedrooms quantity distribution')
    st.sidebar.subheader('Select the Max Bedroom quantity')
    f_bedrooms = st.sidebar.selectbox('Bedrooms', sorted(set(data['bedrooms'].unique())),
                                      index=(len(data['bedrooms'].unique()) - 1))

    c2.subheader('Bathrooms quantity distribution')
    st.sidebar.subheader('Select the Max Bathrooms quantity')
    f_bathrooms = st.sidebar.selectbox('Bathrooms', sorted(set(data['bathrooms'].unique())),
                                       index=(len(data['bathrooms'].unique()) - 1))

    c3, c4= st.columns(2)

    c3.subheader('Houses per Floor')
    st.sidebar.subheader('Select the Max floor per House')
    f_floors = st.sidebar.selectbox('Floors', sorted(set(data['floors'].unique())),
                                    index=(len(data['floors'].unique()) - 1))

    c4.subheader('Houses per Waterfront')
    f_waterfront = st.sidebar.checkbox('Only Houses with Water View')

    df = data[(data['bedrooms'] <= f_bedrooms) & (data['bathrooms'] <= f_bathrooms) & (data['floors'] <= f_floors)]

    if f_waterfront:
        df = df[df['waterfront'] == 1]
    else:
        df = df.copy()

    # --------- QUARTOS POR CASA
    fig = px.histogram(df, x='bedrooms', nbins=50)
    c1.plotly_chart(fig, use_container_width=True)

    # --------- BANHEIROS POR CASA
    fig = px.histogram(df, x='bathrooms', nbins=50)
    c2.plotly_chart(fig, use_container_width=True)

    # --------- ANDARES POR CASA
    fig = px.histogram(df, x='floors', nbins=12)
    c3.plotly_chart(fig, use_container_width=True)

    # --------- WATERFRONT POR CASA
    fig = px.pie(df, values='id', names='waterfront')
    c4.plotly_chart(fig, use_container_width=True)

    return None


def purchase_recommendation(data):
    region_price_median = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()
    region_price_median = region_price_median.rename(columns={'price': 'region_price_median'})

    data = pd.merge(data, region_price_median, on='zipcode', how='inner')
    data['recommendation'] = data[['price', 'region_price_median','condition']].apply(
        lambda x: 'Buy' if (x['price'] < x['region_price_median']) & (x['condition'] >=4) else 'Not Buy', axis=1)

    houses_recommendations = pd.DataFrame(
        data[['id', 'zipcode', 'condition', 'price', 'region_price_median', 'recommendation']].copy())
    csv = houses_recommendations.to_csv().encode('utf-8')
    st.download_button(
        label="Download Purchase Recommendations",
        data=csv,
        file_name='purchase-recommendations.csv',
        mime='text/csv',
    )
    st.dataframe(houses_recommendations, height=300)

    return data


def sell_recommendations(data):
    data = data[data['recommendation'] == 'Buy']
    season_price_median = data[['zipcode', 'seasons', 'price']].groupby(['zipcode', 'seasons']).median().reset_index()
    season_price_median = season_price_median.rename(columns={'price': 'zip_per_region_price_median'})
    data = pd.merge(data, season_price_median, on=['zipcode', 'seasons'], how='left')
    # Preço de venda recomendado
    data['sell_price'] = data[['price', 'zip_per_region_price_median', 'seasons']].apply(
        lambda x: x['price'] * 1.3 if (x['price'] < x['zip_per_region_price_median']) else
        x['price'] * 1.1, axis=1)
    # calculando o lucro
    data['profit'] = round(data['sell_price'] - data['price'], 1)

    sugestion_sell = data[
        ['id', 'price', 'zipcode', 'price_m2', 'zip_per_region_price_median', 'sell_price', 'profit']].copy()

    sugestion_sell.to_csv('sugestion_sell.csv')
    csv = sugestion_sell.to_csv().encode('utf-8')
    st.download_button(
        label="Download Sells Recommendations",
        data=csv,
        file_name='sells-recommendations.csv',
        mime='text/csv',
    )
    st.dataframe(sugestion_sell, height=300)

    return data

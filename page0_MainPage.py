import page2_DataOverview
import page4_Maps
import page1_Welcome
import page3_Recommendations
import streamlit as st
import defs

if __name__ == '__main__':
    st.set_page_config(layout='wide')

    # importando dados
    path = 'kc_house_data.csv'
    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
    data = defs.getdata(path)
    geofile = defs.get_geofile(url)

    # adicionando features e fazendo conversões
    data = defs.set_feature(data)

    # Definindo páginas
    PAGES = {
        "👋 Welcome!": page1_Welcome,
        "🌎 Data Overview": page2_DataOverview,
        "🏠 Recommendations": page3_Recommendations,
        "🗺️ House Maps": page4_Maps,
    }

    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    page.app(data,geofile)

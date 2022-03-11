import streamlit as st
import defs

def app(data, geofile,):

    st.header('Portfolio Density')
    if not st.checkbox('Use full dataset'):
        data = data.sample(500)

    selection = st.radio('Map Type', ['Portfolio', 'Density Price per Region', 'Price Map'])
    if selection == 'Portfolio':
        defs.portfolio_density(data, geofile)
    elif selection == 'Density Price per Region':
        defs.zipcode_price_density(data, geofile)
    elif selection == 'Price Map':
        defs.price_houses(data)

    return None

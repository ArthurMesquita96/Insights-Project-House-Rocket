import defs
import streamlit as st

def app(data, _):

    st.title('Insights Project - House Rocket 🏠')
    st.write("House Rocket is a fictitious real estate agent that wants to use data science to your advantage to find better business opportunities. The Company's Core Business is the purchase of real estate at a low price in order to resell at a higher price and thus ensure profit.")

    st.header('Business Issues')
    st.write('House Rocket seeks to resolve the following business issues:')
    st.markdown('1. What properties should House Rocket buy and at what price?')
    st.markdown('2. Once the house is purchased, when is the best time to sell them and at what price?')

    st.header('About the data')
    st.write('For the solution were considered the reports of property sales prices in the King Country region, including Seattle')
    st.write('The following were evaluated:')

    num_houses = data['id'].unique().size
    num_years = data['date'].dt.year.unique()
    num_zipcode = data['zipcode'].unique().size

    c1, c2, c3, c4 = st.columns(4)
    st.metric(label="Number of houses", value=num_houses)
    st.metric(label="Period", value=f'De Maio de {num_years[0]} a Maio de {num_years[-1]}')
    st.metric(label="Number of zipcods", value=num_zipcode)
    return None
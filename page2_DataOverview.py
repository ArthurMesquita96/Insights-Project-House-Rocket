import streamlit as st
import defs

def app(data,geofile):

    st.title('Data Overview')

    if not st.checkbox('Use the full dataset'):
        data = data.sample(int(len(data)*0.1))

    # Data Overview
    defs.overview_data(data,geofile)

    defs.comercial_distribution(data)

    # Description of Houses Attributes
    defs.attributes_distribution(data)

    return None
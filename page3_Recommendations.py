import defs
import streamlit as st

def app(data, _):

    st.title('Recommendations')
    st.header('Purchase Suggestions')
    st.write('The purchase suggestions were elaborated based on two factors:')
    st.write('    * The property location (zipcode)')
    st.write('    * The average price of properties in a given region')
    st.write('    * The property condition')
    st.write('Properties in good condition that have the purchase price below the average price of properties in the region are considered good buying opportunities and are detailed in the table below')
    st.subheader('Purchase Recommendations_')
    data = defs.purchase_recommendation(data)
    data2 = data[data['recommendation'] == 'Buy']

    if st.checkbox('Click here to see recommended houses'):
        defs.houses_map(data2,'_Houses to Buy_','price','condition',"The graph shows as color the condition of each house. The size represent the houses's price",'Total Houses sugested',len(data[data['recommendation'] == 'Buy']))

    st.header('Sales Suggestions')
    st.write('After the purchase of the properties, the following report is intended to suggest when and at what price the houses should be sold. These recommendations were developed on the basis of two factors')
    st.write('    - The location of the property (zipcode)')
    st.write('    - The season (Summer, Winter, Fall and Spring)')
    st.markdown('**Premises**')
    st.write(        " * For properties with the purchase price _below_ the average price of the region per season, it's suggested the sale with the increase of 30% in value")
    st.write(        ' * For properties with the purchase price above the average price of the region per season is suggested the sale with the increase of 10% in value')
    st.subheader('_Sales Recommendations_')
    data = defs.sell_recommendations(data)
    if st.checkbox('Click here to see the profit per sell'):
        defs.houses_map(data,'Profit per House','price','profit',"Graph shows as color the profit before the sell of each house. The size represent the houses's price",'Expected Profit',f"{int(sum(data['profit']))} dolars")

    return None
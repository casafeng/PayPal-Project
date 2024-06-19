import altair as alt
import pandas as pd 
import streamlit as st 
import datetime 
from datetime import date, timedelta 
import matplotlib.pyplot as plt 

st.set_page_config(page_title="Charts", page_icon="📈")

st.title("Chart Creator")


Payment_Status = st.selectbox(
    'What Payment Status',
    ('All', 'Charge', 'Refund', 'Chargeback')
    )

Payment_Method = st.selectbox(
    'What Payment Method',
    ('All', 'Goods and Service', 'Friends and Family')
    )

Payment_Application = st.selectbox(
    'What Payment Application',
    ('All', 'Desktop', 'Tablet', 'Phone')
    )

Payment_Country = st.selectbox(
    'What Payment Status',
    ('All', 'US', 'UK', 'AU')
    )

today = datetime.now()
days180 = date.today() - timedelta(days = 180)

StartDate = st.date_input("Start Date (Default 180 Days Prior)", days180)
EndDate = st.date_input("End Date (Default Today)", today)

df_pre_clean = st.file_uploader("Selcet CSV File")

if df_pre_clean is not None:
    df_pre_clean = pd.read_csv(df_pre_clean)
else:
    st.stop()

df_pre_clean.drop(['Transaction_ID', 'Auth_code'], axis = 1, inplace = True)
df_pre_clean2 = df_pre_clean[df_pre_clean['Success'] == 1]
df_pre_clean2['Transaction_Notes'].fillna('N/A', inplace = True)
df_pre_clean2['Day'] = pd.to_datetime(df_pre_clean2['Day'])
df = df_pre_clean2.loc[:, ['Total', 'Transaction_Type', 'Type', 'Country', 'Source', 'Day', 'Customer_Name','Transaction_Notes']]

df['int_created_date'] = df['Day'].dt.year * 100 + df['Day'].dt.month

# Payment_Status

if Payment_Status == 'Charge':
    df = df[df['Type'] == 'Charge']
elif Payment_Status == 'Refund':
    df = df[df['Type'] == 'Refund']
elif Payment_Status == 'Chargeback':
    df = df[df['Type'] == 'Chargeback']
else:
    pass

# Payment_Method

if Payment_Method == 'Goods and Service':
    df = df[df['Transaction_Type'] == 'Goods and Service']
elif Payment_Method == 'Friends and Family':
    df = df[df['Transaction_Type'] == 'Friends and Family']
else:
    pass

# Payment_Application

if Payment_Application == 'Desktop':
    df = df[df['Source'] == 'Desktop']
elif Payment_Application == 'Tablet':
    df = df[df['Source'] == 'Tablet']
elif Payment_Application == 'Phone':
    df = df[df['Source'] == 'Phone']
else:
    pass

# Payment_Country

if Payment_Country == 'US':
    df = df[df['Country'] == 'US']
elif Payment_Country == 'UK':
    df = df[df['Country'] == 'UK']
elif Payment_Country == 'AU':
    df = df[df['Country'] == 'AU']
else:
    pass

StartDate = pd.to_datetime(StartDate)
EndDate = pd.to_datetime(EndDate)

df = df[(df['Day'] >= StartDate) & (df['Day'] <= EndDate)]

chart1 = alt.Chart(df).mark_bar().encode(
    alt.X("Total: Q", bin = True),
    y = 'count()'
).properties(
    title={
        "text": ["Count of Transactions"],
        "subtitle": [f"Payment Status: {Payment_Status}", f"Payment Method: {Payment_Method}", f"Payment Application: {Payment_Application}", f"Payment Country: {Payment_Country}", f"Start Date: {StartDate}", f"End Date: {EndDate}"]
    }, 
    width = 800,
    height = 500
)

chart2 = alt.Chart(df).mark_boxplot(extent = 'min-max').encode(
    x = 'int_created_date:O',
    y = 'Total:Q'
).properties(
    title={
        "text": ["Box/Whisker By Month"],
        "subtitle": [f"Payment Status: {Payment_Status}", f"Payment Method: {Payment_Method}", f"Payment Application: {Payment_Application}", f"Payment Country: {Payment_Country}", f"Start Date: {StartDate}", f"End Date: {EndDate}"]
    }, 
    width = 800,
    height = 500
)

bar3 = alt.Chart(df).mark_bar().encode(
    x = alt.X('int_created_date:O', title = 'Date'),
    y = alt.Y('sum(Total):Q', title = 'Total'),
    color = alt.Color('Type:N', title = 'Payment Type')
)

chart3 = (bar3).properties(
    title={
        "text": ["Box Plot Sum Transactions By Month"],
        "subtitle": [f"Payment Status: {Payment_Status}", f"Payment Method: {Payment_Method}", f"Payment Application: {Payment_Application}", f"Payment Country: {Payment_Country}", f"Start Date: {StartDate}", f"End Date: {EndDate}"]
    }, 
    width = 800,
    height = 500
)

bar4 = alt.Chart(df).mark_bar().encode(
    x = alt.X('int_created_date:O', title = 'Date'),
    y = alt.Y('count(Total):Q', title = 'Total'),
    color = alt.Color('Type:N', title = 'Payment Type')
)

chart4 = (bar4).properties(
    title={
        "text": ["Box Plot Count Transactions By Month"],
        "subtitle": [f"Payment Status: {Payment_Status}", f"Payment Method: {Payment_Method}", f"Payment Application: {Payment_Application}", f"Payment Country: {Payment_Country}", f"Start Date: {StartDate}", f"End Date: {EndDate}"]
    }, 
    width = 800,
    height = 500
)
tab1, tab2, tab3 , tab4 = st.tabs(["Histogram", "Box/Whisker", "Box Plot Sum", "Box Plot Count"])

with tab1:
    st.altair_chart(chart1, use_container_width = True)
with tab2:
    st.altair_chart(chart2, use_container_width = True)
with tab3:
    st.altair_chart(chart3, use_container_width = True)
with tab4:
    st.altair_chart(chart4, use_container_width = True)
    

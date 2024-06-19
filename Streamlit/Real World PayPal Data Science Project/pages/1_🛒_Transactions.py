
import streamlit as st
import pandas as pd
import numpy as np 
import datetime 
from datetime import date, timedelta 
import xlsxwriter
import io

st.set_page_config(page_title="Transactions", page_icon="🛒")

st.title("Transaction Breakdown")

filename = st.text_input("Filename", key='filename')
first_name = st.text_input("Enter Name", key="firstname1")
highticket_string = st.number_input("Enter High TIcket Integer Only")
uploaded_file = st.file_uploader("Please Upload a CSV File", type=['csv'])

if uploaded_file is not None:

    high_ticket_val = int(highticket_string)
    df_pre_clean = pd.read_csv(uploaded_file)

    buffer = io.ByterIO()



    # IMPORT DATA
    # df_pre_clean = pd.read_csv('data collection/Paypal_Transactions3.csv')
    # df_pre_clean.head()

    # DROP COLUMNS
    df_pre_clean.drop(['Transaction_ID', 'Auth_code'], axis = 1, inplace = True)
    df_pre_clean2 = df_pre_clean[df_pre_clean['Success'] == 1]

    # LOOK SPECIFICALLY AT TRANSACTION NOTES
    df_pre_clean2['Transaction_Notes'].fillna('N/A', inplace = True)

    # TURN DAY INTO DAYTIME USING PANDAS
    df_pre_clean2['Day'] = pd.to_datetime(df_pre_clean2['Day'])

    # CHANGE COLUMNS
    # df_pre_clean2.columns
    df = df_pre_clean2.loc[:, ['Total', 'Transaction_Type', 'Type', 'Country', 'Source', 'Day', 'Customer_Name','Transaction_Notes']]

    # BUILD DIFFERENT CALCULATIONS 
    totalsum = np.sum(df['Total'])
    total_transactions = df['Type'].count()
    mean_transactions = np.mean(df['Total'])
    median_transactions = np.median([df['Total']])
    max_transactions = np.max(df['Total'])

    # total_unique_customers_names = df['Customer_Name'].nunique()

    # BUILD NEW DATA FRAMES 
    charge_only_transactions = df[df['Type'] == 'Charge']
    refund_only_transactions = df[df['Type'] == 'Refund']
    chargeback_only_transactions = df[df['Type'] == 'Chargeback']

    # SET 90 DAYS AND 180 DAYS
    days90 = pd.to_datetime(date.today() - timedelta(days=90))
    days180 = pd.to_datetime(date.today() - timedelta(days=180))

    # TAKE A LOOK AT CHARGES 
    charge_total = np.sum(charge_only_transactions['Total'])
    charge_90days = np.sum(charge_only_transactions[charge_only_transactions['Day'] > days90]['Total'])
    charge_180days = np.sum(charge_only_transactions[charge_only_transactions['Day'] > days180]['Total'])

    # SIMILARLY WITH REFUND AND CHARGE BACKS 
    refund_total = np.sum(refund_only_transactions['Total'])
    refund_90days = np.sum(refund_only_transactions[refund_only_transactions['Day'] > days90]['Total'])
    refund_180days = np.sum(refund_only_transactions[refund_only_transactions['Day'] > days180]['Total'])

    chargeback_total = np.sum(chargeback_only_transactions['Total'])
    chargeback_90days = np.sum(chargeback_only_transactions[chargeback_only_transactions['Day'] > days90]['Total'])
    chargeback_180days = np.sum(chargeback_only_transactions[chargeback_only_transactions['Day'] > days180]['Total'])

    # CALCULATION REFUND RATE 
    refund_rate_lifetime = (refund_total/ charge_total)
    refund_rate_90days = (refund_90days/ charge_90days)
    refund_rate_180days = (refund_180days/ charge_180days)

    # CALCULATION CHARGE BACK RATE
    chargeback_rate_lifetime = (chargeback_total/ charge_total)
    chargeback_rate_90days = (chargeback_90days/ charge_90days)
    chargeback_rate_180days = (chargeback_180days/ charge_180days)

    # BUILD PIVOT TABLES 
    pivot_table_names = pd.pivot_table(df, index = ['Customer_Name'], aggfunc = {'Total': np.sum, 'Customer_Name': 'count'})
    pivot_table_names = pivot_table_names.rename(columns={'Customer_Name': 'count_of_total', 'Total': 'sum_of_total'})
    pivot_table_names = pivot_table_names.loc[:, ['sum_of_total', 'count_of_total']]
    total_unique_customers = pivot_table_names['sum_of_total'].count()

    average_transactions_count_per_customer_name = np.mean(pivot_table_names['count_of_total'])
    average_transactions_sum_per_customer_name = np.mean(pivot_table_names['sum_of_total'])

    # LOOK AT TRANSACTION TYPES AND BUILD PIVOT TABLE 
    pivot_table_transaction_types = pd.pivot_table(df, index = ['Transaction_Type'], aggfunc = {'Transaction_Type': 'count', 'Total': np.sum})
    pivot_table_transaction_types['total_percent'] = (pivot_table_transaction_types['Total']/totalsum).apply('{:.2%}'.format)

    # PER COUNTRY 
    pivot_table_transaction_country = pd.pivot_table(df, index = ['Country'], aggfunc = {'Country': 'count', 'Total': np.sum})
    pivot_table_transaction_country['total_percent'] = (pivot_table_transaction_country['Total']/totalsum).apply('{:.2%}'.format)

    # LOOK AT NAME SEARCH 
    # first_name = 'Angelo'
    name_final = df[df['Customer_Name'].str.contains(first_name, case = False)]

    # LOOK AT NOTE SECTION 
    payment_note = df[df['Transaction_Notes'].isna()==False]
    flagged_words = 'raffle|razz|lottery'
    payment_note_final = df[df['Transaction_Notes'].str.contains(flagged_words, case = False)]

    # high_ticket_val = 3500
    high_ticket = df[df['Total'] >= high_ticket_val].copy()
    high_ticket = high_ticket.sort_values(by ='Total', ascending = False)


    # DUPLICATE
    dup = df.copy()
    dup['Customer_Name_next'] = dup['Customer_Name'].shift(1)
    dup['Customer_Name_prev'] = dup['Customer_Name'].shift(-1)

    # LOOK DATES SIDE
    dup['created_at_day'] = dup['Day']
    dup['created_at_day_prev'] = dup['Day'].shift(-1)
    dup['created_at_day_next'] = dup['Day'].shift(1)

    # LOOK IF THERE ARE MULTIPLE TRANSACTIONS ON THE SAME DAY
    # dup2 = dup.query('created_at_day == created_at_day_prev | created_at_day == created_at_day_next')
    # dup3 = dup2.query('Customer_Name == Customer_Name_next | Customer_Name == Customer_Name_prev')

    dup3 = dup.query('(created_at_day == created_at_day_prev | created_at_day == created_at_day_next) & (Customer_Name == Customer_Name_next | Customer_Name == Customer_Name_prev)')

    df_calc = pd.DataFrame({
        'totalsum':[totalsum],
        'mean_transactions':    [mean_transactions],
        'median_transactions':   [median_transactions],
        'max_transactions':      [max_transactions],
        'total_transactions':   [total_transactions],
        'charge_total':         [charge_total],
        'charge_90days':        [charge_90days],
        'charge_180days':       [charge_180days],
        'refund_total':         [refund_total],
        'refund_90days':        [refund_90days],
        'refund_180days':       [refund_180days],
        'chargeback_total':     [chargeback_total],
        'chargeback_90days':    [chargeback_90days],
        'chargeback_180days':   [chargeback_180days],
        'refund_rate_lifetime': [refund_rate_lifetime],
        'refund_rate_90days':   [refund_rate_90days],
        'refund_rate_180days':   [refund_rate_180days],
        'chargeback_rate_lifetime':  [chargeback_rate_lifetime],
        'chargeback_rate_90days':  [chargeback_rate_90days],
        'chargeback_rate_180days':  [chargeback_rate_180days],
        'total_unique_customers_names':  [total_unique_customers],
        'average_transactions_count_per_customer_name':  [average_transactions_count_per_customer_name],
        'average_transactions_sum_per_customer_name':  [average_transactions_sum_per_customer_name],
        '90 Days':  [days90],
        '180 Days':  [days180],
    })

    format_mapping = {
        "totalsum": '${:,.2f}',
        "mean_transactions": '${:,.2f}',
        "median_transactions": '${:,.2f}',
        "max_transactions": '${:,.2f}',
        "total_transactions": '${:,.0f}',
        "charge_total": '${:,.2f}',
        "charge_90days": '${:,.2f}',
        "charge_180days": '${:,.2f}',
        "refund_total": '${:,.2f}',
        "refund_90days": '${:,.2f}',
        "refund_180days": '${:,.2f}',
        "refund_rate_lifetime": '${:,.2%}',
        "refund_rate_90days": '${:,.2%}',
        "refund_rate_180days": '${:,.2%}',
        "chargeback_total": '${:,.2f}',
        "chargeback_90days": '${:,.2f}',
        "chargeback_180days": '${:,.2f}',
        "chargeback_rate_lifetime": '${:,.2%}',
        "chargeback_rate_90days": '${:,.2%}',
        "chargeback_rate_180days": '${:,.2%}',
        "total_unique_customers_names": '${:,.0f}',
        "average_transactions_count_per_customer_name": '${:,.2f}',
        "average_transactions_sum_per_customer_name": '${:,.2f}'
    }

    for key, value in format_mapping.items():
        df_calc[key] = df_calc[key].apply(value.format)

    with pd.ExcelWriter(buffer, engine='xlswriter') as writer:
        df.to_excel(writer, sheet_name='Clean_Data')
        df_calc.to_excel(writer, sheet_name='Calculations')
        pivot_table_names.to_excel(writer, sheet_name='Names')
        pivot_table_transaction_types.to_excel(writer, sheet_name='Transaction_Type')
        pivot_table_transaction_country.to_excel(writer, sheet_name='Countries')
        payment_note_final.to_excel(writer, sheet_name='Payment_Notes')
        high_ticket.to_excel(writer, sheet_name='High_Ticket')
        name_final.to_excel(writer, sheet_name='Name_checker')
        dup3.to_excel(writer, sheet_name='Double_Transactions')

        writer.close()

        st.download_button(
            label = 'Download Excel File',
            data = buffer,
            file_name= f"{st.session_state.file_name}.xlsx",
            mime="application/vnd.ms-excel"
        )
    
else:
    st.warning("You need to uplead a csv file")


        
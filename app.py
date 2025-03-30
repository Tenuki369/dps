import streamlit as st
import pandas as pd
import plotly.express as px

def clean_column(df, column_name):
    df[column_name] = df[column_name].astype(str).str.replace('%', '').apply(pd.to_numeric, errors='coerce')
    return df

def load_data(uploaded_file):
    # Load the file into pandas dataframe
    df_raw = pd.read_excel(uploaded_file, header=1)  # Headers are now in the second row (index 1)
    
    # Clean the required columns
    df_raw = clean_column(df_raw, "Gamma")
    df_raw = clean_column(df_raw, "Impl Vol")
    
    # Separate the data for calls and puts based on the "Strike" column
    calls_data = df_raw[df_raw['Strike'] <= 100]  # Assuming calls have strikes less than or equal to 100
    puts_data = df_raw[df_raw['Strike'] > 100]    # Assuming puts have strikes greater than 100
    
    return calls_data, puts_data

def plot_gamma_exposure(calls, puts):
    # Ensure that the data contains the required columns
    if 'Strike' in calls.columns and 'Gamma' in calls.columns:
        # Plot for Calls
        fig_calls = px.line(calls, x='Strike', y='Gamma', title="Gamma Exposure by Strike (Calls)")
        st.plotly_chart(fig_calls)
    else:
        st.error("The required columns ('Strike' and 'Gamma') are missing in the Calls data.")
    
    if 'Strike' in puts.columns and 'Gamma' in puts.columns:
        # Plot for Puts
        fig_puts = px.line(puts, x='Strike', y='Gamma', title="Gamma Exposure by Strike (Puts)")
        st.plotly_chart(fig_puts)
    else:
        st.error("The required columns ('Strike' and 'Gamma') are missing in the Puts data.")

def main():
    st.title("Options Gamma Dashboard")

    # File uploader widget
    uploaded_file = st.file_uploader("Upload your options chain Excel file", type=["xlsx"])

    if uploaded_file is not None:
        # Load and clean the data
        calls_data, puts_data = load_data(uploaded_file)
        
        # Display the data
        st.subheader("Data Preview")
        st.write(calls_data.head())  # Preview the first few rows of Calls data
        st.write(puts_data.head())   # Preview the first few rows of Puts data

        # Call the plotting function
        plot_gamma_exposure(calls_data, puts_data)

if __name__ == "__main__":
    main()

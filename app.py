import streamlit as st
import pandas as pd
import plotly.express as px

# Function to clean columns (removing '%' and converting to numeric)
def clean_column(df, column_name):
    if column_name in df.columns:
        df[column_name] = df[column_name].astype(str).str.replace('%', '').apply(pd.to_numeric, errors='coerce')
        # Check for NaN values and replace them with 0 or any other placeholder value
        df[column_name] = df[column_name].fillna(0)
    else:
        st.warning(f"Column '{column_name}' is missing from the data!")
    return df

# Function to load data (assuming the uploaded file is loaded correctly)
def load_data(uploaded_file):
    df_raw = pd.read_excel(uploaded_file, header=1)  # Header starts from row 2 (index 1)
    return df_raw

# Streamlit Upload section
uploaded_file = st.file_uploader("Upload Options Chain Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Load and clean data
    df = load_data(uploaded_file)
    
    # Clean specific columns
    df = clean_column(df, "Gamma")
    df = clean_column(df, "Impl Vol")
    df = clean_column(df, "Strike")  # Ensure no NaN values
    
    # Filter Calls and Puts Data (assuming data for calls is on the left of Strike and puts on the right)
    calls_data = df[df['Strike'] <= df['Strike'].max() // 2]  # You can adjust this filter logic based on your needs
    puts_data = df[df['Strike'] > df['Strike'].max() // 2]

    # Gamma Exposure for Calls
    fig_calls = px.line(calls_data, x='Strike', y='Gamma', title="Gamma Exposure by Strike (Calls)")
    fig_calls.show()
    
    # Gamma Exposure for Puts
    fig_puts = px.line(puts_data, x='Strike', y='Gamma', title="Gamma Exposure by Strike (Puts)")
    fig_puts.show()

    # 3D Scatter Plot - Gamma vs. Strike vs. Implied Volatility for Calls
    fig_calls_4d = px.scatter_3d(calls_data, x='Strike', y='Gamma', z='Impl Vol', color='Impl Vol',
                                 title="3D Visualization of Calls")
    fig_calls_4d.show()

    # 3D Scatter Plot - Gamma vs. Strike vs. Implied Volatility for Puts
    fig_puts_4d = px.scatter_3d(puts_data, x='Strike', y='Gamma', z='Impl Vol', color='Impl Vol',
                                title="3D Visualization of Puts")
    fig_puts_4d.show()

    # 5D Visualization - Plotting the additional dimensions based on your requirements
    fig_calls_5d = px.scatter_3d(calls_data, x='Strike', y='Gamma', z='Impl Vol', color='Impl Vol',
                                 size='Volume', symbol='Delta', title="5D Visualization of Calls")
    fig_calls_5d.show()

    fig_puts_5d = px.scatter_3d(puts_data, x='Strike', y='Gamma', z='Impl Vol', color='Impl Vol',
                                size='Volume', symbol='Delta', title="5D Visualization of Puts")
    fig_puts_5d.show()

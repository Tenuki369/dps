import pandas as pd
import plotly.express as px
import streamlit as st

# Load and clean the data
def load_data(file):
    df = pd.read_excel(file, header=1)
    return df

# Clean column names by stripping extra spaces and replacing symbols like '%'
def clean_column(df, column_name):
    df[column_name] = df[column_name].astype(str).str.replace('%', '').apply(pd.to_numeric, errors='coerce')
    return df

# Plotting Gamma Exposure by Strike (with Calls and Puts)
def plot_gamma_exposure(calls_data, puts_data):
    # Gamma Exposure for Calls
    fig_calls = px.line(calls_data, x="Strike", y="Gamma", title="Gamma Exposure by Strike (Calls)")

    # Gamma Exposure for Puts
    fig_puts = px.line(puts_data, x="Strike", y="Gamma", title="Gamma Exposure by Strike (Puts)")

    # 4D Visualization for Calls: Using Volume as size and color
    fig_calls_4d = px.scatter_3d(
        calls_data, x="Strike", y="Gamma", z="Impl Vol",
        color="Volume", size="Volume", title="Gamma Exposure in 4D (Calls)"
    )
    fig_calls_4d.update_traces(marker=dict(size=5))

    # 4D Visualization for Puts: Using Volume as size and color
    fig_puts_4d = px.scatter_3d(
        puts_data, x="Strike", y="Gamma", z="Impl Vol",
        color="Volume", size="Volume", title="Gamma Exposure in 4D (Puts)"
    )
    fig_puts_4d.update_traces(marker=dict(size=5))

    # 5D Visualization: Adding Expiry Date (Exp) as Animation Frame
    fig_calls_5d = px.scatter_3d(
        calls_data, x="Strike", y="Gamma", z="Impl Vol",
        color="Volume", animation_frame="Exp", title="Gamma Exposure by Strike (Calls) with Expiry"
    )
    fig_puts_5d = px.scatter_3d(
        puts_data, x="Strike", y="Gamma", z="Impl Vol",
        color="Volume", animation_frame="Exp", title="Gamma Exposure by Strike (Puts) with Expiry"
    )

    return fig_calls, fig_puts, fig_calls_4d, fig_puts_4d, fig_calls_5d, fig_puts_5d

# Streamlit UI setup
st.title("Options Gamma Dashboard")

uploaded_file = st.file_uploader("Upload your options chain Excel file", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # Cleaning data
    df = clean_column(df, "Gamma")
    df = clean_column(df, "Impl Vol")
    df = clean_column(df, "OI")
    
    # Splitting data into Calls and Puts
    calls_data = df[df["Strike"] <= df["Strike"].median()]
    puts_data = df[df["Strike"] > df["Strike"].median()]
    
    # Plot Gamma Exposure
    fig_calls, fig_puts, fig_calls_4d, fig_puts_4d, fig_calls_5d, fig_puts_5d = plot_gamma_exposure(calls_data, puts_data)
    
    # Displaying the charts
    st.plotly_chart(fig_calls)
    st.plotly_chart(fig_puts)
    st.plotly_chart(fig_calls_4d)
    st.plotly_chart(fig_puts_4d)
    st.plotly_chart(fig_calls_5d)
    st.plotly_chart(fig_puts_5d)


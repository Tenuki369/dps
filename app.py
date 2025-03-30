import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Options Gamma Dashboard")

# Upload file
uploaded_file = st.file_uploader("Upload Options Chain Excel File (.xlsx)", type="xlsx")

if uploaded_file:
    # Read the raw data
    df_raw = pd.read_excel(uploaded_file, header=None)
    st.subheader("📄 Raw Preview")
    st.write("First 20 Rows (no headers):")
    st.dataframe(df_raw.head(20))

    st.subheader("🧠 Headers from Row 2 (index 1)")
    try:
        df_header = pd.read_excel(uploaded_file, header=1, nrows=1)
        st.write("Detected Column Names:")
        st.write(df_header.columns.tolist())
    except Exception as e:
        st.error(f"Failed to read headers from row 2: {e}")

    # Load the data with headers set at row 2
    df = pd.read_excel(uploaded_file, header=1)
    st.subheader("📊 Cleaned Data Preview")
    
    # Clean data by removing or replacing NaN values
    df = df.dropna(subset=['Gamma', 'Impl Vol'])  # Drop rows with NaN in critical columns
    df['Gamma'] = pd.to_numeric(df['Gamma'], errors='coerce')  # Ensure Gamma is numeric
    df['Impl Vol'] = pd.to_numeric(df['Impl Vol'], errors='coerce')  # Ensure Impl Vol is numeric

    # Replace any remaining NaN values after conversion
    df.fillna(0, inplace=True)

    # Display cleaned dataframe preview
    st.dataframe(df.head(20))

    # Gamma Exposure by Strike
    st.subheader("📈 Gamma Exposure by Strike")
    try:
        fig = px.scatter(df, x="Strike", y="Gamma", title="Gamma Exposure vs Strike")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating Gamma Exposure plot: {e}")

    # Implied Volatility Surface
    st.subheader("📉 Implied Volatility Surface")
    try:
        fig = px.scatter(df, x="Strike", y="Impl Vol", size="Open.Int.", title="Implied Volatility vs Strike (Bubble size: OI)")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating Implied Volatility plot: {e}")

    # Gamma Flip Visualization
    st.subheader("🔄 Gamma Flip Visualization")
    try:
        gamma_flip = df[df['Gamma'] == df['Gamma'].min()]['Strike'].values[0]
        st.write(f"Gamma Flip is at Strike: {gamma_flip}")
    except Exception as e:
        st.error(f"Error generating Gamma Flip visualization: {e}")

    # Multi-Dimensional 3D Visualization
    st.subheader("🌐 Multi-Dimensional 3D Visualization")
    try:
        fig = px.scatter_3d(df, x="Strike", y="Gamma", z="Impl Vol", size="Open.Int.", color="Strike", title="3D Plot (Gamma, Implied Volatility, Open Interest)")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating 3D plot: {e}")

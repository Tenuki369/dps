import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns

st.set_page_config(layout="wide")
st.title("📊 Options Gamma Dashboard - Column Inspector")

uploaded_file = st.file_uploader("Upload Options Chain Excel File (.xlsx)", type="xlsx")

if uploaded_file:
    st.subheader("📄 Raw Preview")
    df_raw = pd.read_excel(uploaded_file, header=None)
    st.write("First 20 Rows (no headers):")
    st.dataframe(df_raw.head(20))

    st.subheader("🧠 Headers from Row 2 (index 1)")
    try:
        df_header = pd.read_excel(uploaded_file, header=1, nrows=1)
        st.write("Detected Column Names:")
        st.write(df_header.columns.tolist())
    except Exception as e:
        st.error(f"Failed to read headers from row 2: {e}")

    st.subheader("📊 Data Visualization")
    
    # Load the data with proper headers
    df = pd.read_excel(uploaded_file, header=1)
    
    # Strip any extra spaces from column names
    df.columns = df.columns.str.strip()
    
    # Ensure all necessary columns are present
    required_columns = ['Gamma', 'Impl Vol.', 'OI', 'Strike', 'Exp']
    for column in required_columns:
        if column not in df.columns:
            st.error(f"Missing expected column: {column}")
            st.stop()

    # Clean the data by removing any unwanted characters
    def clean_column(col):
        return pd.to_numeric(df[col].astype(str).str.replace('%', '').apply(pd.to_numeric, errors='coerce'))

    # Clean relevant columns
    df["Gamma"] = clean_column("Gamma")
    df["Impl Vol."] = clean_column("Impl Vol.")
    df["OI"] = clean_column("OI")

    # Implied Volatility Surface Visualization
    st.subheader("Implied Volatility Surface")
    fig = px.scatter(df, x="Strike", y="Impl Vol.", color="Exp", size="OI",
                     title="Implied Volatility vs Strike",
                     labels={"Impl Vol.": "Implied Volatility", "Strike": "Strike Price"})
    st.plotly_chart(fig)
    
    # Gamma Flip Visualization
    st.subheader("Gamma Flip Visualization")
    gamma_flip = df[df['Gamma'] == df['Gamma'].min()]
    st.write(f"Gamma Flip is at Strike: {gamma_flip['Strike'].values[0]}")
    fig2 = px.scatter(gamma_flip, x="Strike", y="Gamma", size="OI", color="Exp",
                      title="Gamma Flip Visualization",
                      labels={"Gamma": "Gamma Exposure", "Strike": "Strike Price"})
    st.plotly_chart(fig2)
    
    # Multi-Dimensional 3D Visualization
    st.subheader("Multi-Dimensional 3D Visualization")
    fig3 = px.scatter_3d(df, x="Strike", y="Gamma", z="Impl Vol.",
                         color="Exp", size="OI", title="3D Visualization of Options Data")
    st.plotly_chart(fig3)

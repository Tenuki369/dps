import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Function to clean columns (to convert values to numeric after removing unwanted characters like '%')
def clean_column(df, column_name):
    df[column_name] = df[column_name].astype(str).str.replace('%', '').apply(pd.to_numeric, errors='coerce')
    return df

# Function to load and clean data
def load_data(uploaded_file):
    # Read the data
    df_raw = pd.read_excel(uploaded_file, header=None)
    headers = df_raw.iloc[0]
    df = df_raw[1:]
    df.columns = headers

    # Clean specific columns
    df = clean_column(df, "Gamma")
    df = clean_column(df, "Impl Vol")
    df = clean_column(df, "OI")
    
    return df

# Data upload
uploaded_file = st.file_uploader("Upload Options Chain Excel File (.xlsx)", type="xlsx")

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("### Data Preview", df)

    # Create visualizations
    st.write("### Gamma Exposure by Strike")
    fig = plt.figure(figsize=(8, 6))
    sns.lineplot(data=df, x="Strike", y="Gamma")
    plt.title("Gamma Exposure by Strike")
    st.pyplot(fig)

    st.write("### Implied Volatility Surface")
    fig2 = plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x="Strike", y="Impl Vol", size="OI", sizes=(10, 200), hue="OI", palette="viridis")
    plt.title("Implied Volatility Surface")
    st.pyplot(fig2)

    # Gamma Flip visualization
    st.write("### Gamma Flip Visualization")
    gamma_flip = df[df["Gamma"] == df["Gamma"].min()]
    st.write("Gamma Flip is at Strike:", gamma_flip["Strike"].values[0])

    # Multi-Dimensional 3D Visualization
    st.write("### Multi-Dimensional 3D Visualization")
    fig3 = px.scatter_3d(df, x='Strike', y='Gamma', z='Impl Vol', color='OI', size='OI', opacity=0.7)
    fig3.update_layout(scene=dict(xaxis_title='Strike', yaxis_title='Gamma', zaxis_title='Impl Vol'))
    st.plotly_chart(fig3)

    # Handle missing columns
    if 'Impl Vol' not in df.columns:
        st.error("Missing expected column: Impl Vol")
    if 'OI' not in df.columns:
        st.error("Missing expected column: OI")
    if 'Gamma' not in df.columns:
        st.error("Missing expected column: Gamma")

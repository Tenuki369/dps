import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Set page configuration
st.set_page_config(layout="wide")

# Title of the dashboard
st.title("📊 Options Gamma Dashboard")

# File uploader for Excel files
uploaded_file = st.file_uploader("Upload Options Chain Excel File (.xlsx)", type="xlsx")

# Check if file is uploaded
if uploaded_file:
    # Reading the Excel file into a pandas DataFrame
    df_raw = pd.read_excel(uploaded_file, header=None)
    st.subheader("📄 Raw Preview")
    st.write("First 20 Rows (no headers):")
    st.dataframe(df_raw.head(20))

    # Headers from Row 2 (index 1)
    st.subheader("🧠 Headers from Row 2 (index 1)")
    try:
        df_header = pd.read_excel(uploaded_file, header=1, nrows=1)
        st.write("Detected Column Names:")
        st.write(df_header.columns.tolist())
    except Exception as e:
        st.error(f"Failed to read headers from row 2: {e}")

    # Read the file again with correct header
    df = pd.read_excel(uploaded_file, header=1)

    # Cleaning the data
    try:
        # Clean 'Impl Vol' column (remove '%' and convert to float)
        df["Impl Vol"] = pd.to_numeric(df["Impl Vol"].replace('%', '', regex=True), errors='coerce')
        df["Impl Vol"].fillna(0, inplace=True)  # Replace NaN with 0 for missing values
        
        # Keep 'Gamma' as is (if it's already numeric)
        df["Gamma"] = pd.to_numeric(df["Gamma"], errors='coerce')
        df["Gamma"].fillna(0, inplace=True)  # Replace NaN with 0 for missing values
        
        # Convert other columns as necessary
        df["Strike"] = pd.to_numeric(df["Strike"], errors='coerce')
        df["Open.Int"] = pd.to_numeric(df["Open.Int"], errors='coerce')
        df["Bid"] = pd.to_numeric(df["BID"], errors='coerce')
        df["Ask"] = pd.to_numeric(df["ASK"], errors='coerce')

        st.success("Data cleaned successfully!")

    except Exception as e:
        st.error(f"Error cleaning data: {e}")
    
    # Display the cleaned dataframe for preview
    st.subheader("📊 Cleaned Data Preview")
    st.dataframe(df.head(20))

    # Gamma Exposure by Strike
    st.subheader("📈 Gamma Exposure by Strike")
    try:
        sns.lineplot(x="Strike", y="Gamma", data=df)
        plt.title('Gamma Exposure by Strike')
        plt.xlabel('Strike')
        plt.ylabel('Gamma')
        st.pyplot(plt)

    except Exception as e:
        st.error(f"Error generating Gamma Exposure plot: {e}")

    # Implied Volatility Surface
    st.subheader("📉 Implied Volatility Surface")
    try:
        sns.scatterplot(x="Strike", y="Impl Vol", size="Open.Int", data=df)
        plt.title('Volatility vs Strike (Bubble size: OI)')
        plt.xlabel('Strike')
        plt.ylabel('Implied Vol')
        st.pyplot(plt)

    except Exception as e:
        st.error(f"Error generating Implied Volatility plot: {e}")
        
    # Gamma Flip Visualization
    st.subheader("📍 Gamma Flip Visualization")
    try:
        # Example: Filter where Gamma is at its minimum (could be adjusted based on your requirements)
        gamma_flip = df[df["Gamma"] == df["Gamma"].min()]["Strike"].values[0]
        st.write(f"Gamma Flip is at Strike: {gamma_flip}")
        
    except Exception as e:
        st.error(f"Error in Gamma Flip visualization: {e}")

    # Multi-Dimensional 3D Plot using Plotly
    st.subheader("📐 Multi-Dimensional 3D Visualization")

    try:
        # Creating a 3D scatter plot with Plotly (using 'Strike', 'Impl Vol', and 'Gamma' for axes)
        fig = px.scatter_3d(df, x='Strike', y='Impl Vol', z='Gamma',
                            color='Open.Int', size='Open.Int', opacity=0.7,
                            title="3D View: Strike vs Impl Vol vs Gamma",
                            labels={'Strike': 'Strike Price', 'Impl Vol': 'Implied Volatility', 'Gamma': 'Gamma Exposure'})
        
        fig.update_layout(scene=dict(xaxis_title='Strike',
                                     yaxis_title='Implied Volatility',
                                     zaxis_title='Gamma Exposure'))
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error generating 3D plot: {e}")
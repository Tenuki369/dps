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
        detected_columns = df_header.columns.tolist()  # Store detected column names
        st.write(detected_columns)
    except Exception as e:
        st.error(f"Failed to read headers from row 2: {e}")
        #  Important: Return here to prevent further errors if headers are not read
        return

    # Load the data with headers set at row 2
    df = pd.read_excel(uploaded_file, header=1)
    st.subheader("📊 Cleaned Data Preview")

    # 1. Print the actual column names in the DataFrame
    st.write("Actual DataFrame Columns:")
    st.write(df.columns.tolist())

    # 2. Normalize column names (lowercase and remove spaces) for comparison
    df.columns = df.columns.str.lower().str.replace(' ', '')
    
    # 3. Define the columns we want to keep (normalized)
    required_columns = ['gamma', 'implvol', 'open.int.']
    
    # 4. Drop rows with NaN in the required columns
    try:
        df = df.dropna(subset=required_columns)
    except KeyError as e:
        st.error(f"KeyError: {e}.  Please check the column names in your Excel file.  The application is expecting 'Gamma', 'Impl Vol', and 'Open Int' (case-insensitive, spaces ignored).")
        return # Stop processing if there is a KeyError

    # Ensure that the required columns are present *before* proceeding.
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Required column '{col}' not found.  Please check the column names in your Excel file.")
            return

    df['gamma'] = pd.to_numeric(df['gamma'], errors='coerce')  # Ensure Gamma is numeric
    df['implvol'] = pd.to_numeric(df['implvol'], errors='coerce')  # Ensure Impl Vol is numeric
    df['open.int.'] = pd.to_numeric(df['open.int.'], errors='coerce')  # Ensure Open.Int is numeric
    
    # Replace any remaining NaN values after conversion
    df.fillna(0, inplace=True)

    # Display cleaned dataframe preview
    st.dataframe(df.head(20))

    # Gamma Exposure by Strike
    st.subheader("📈 Gamma Exposure by Strike")
    try:
        fig = px.scatter(df, x="Strike", y="gamma", title="Gamma Exposure vs Strike")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating Gamma Exposure plot: {e}")

    # Implied Volatility Surface
    st.subheader("📉 Implied Volatility Surface")
    try:
        fig = px.scatter(df, x="Strike", y="implvol", size="open.int.", title="Implied Volatility vs Strike (Bubble size: OI)")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating Implied Volatility plot: {e}")

    # Gamma Flip Visualization
    st.subheader("🔄 Gamma Flip Visualization")
    try:
        gamma_flip = df[df['gamma'] == df['gamma'].min()]['Strike'].values[0]
        st.write(f"Gamma Flip is at Strike: {gamma_flip}")
    except Exception as e:
        st.error(f"Error generating Gamma Flip visualization: {e}")

    # Multi-Dimensional 3D Visualization
    st.subheader("🌐 Multi-Dimensional 3D Visualization")
    try:
        # Debugging: Inspect Open.Int. column
        st.write("Open.Int. column info:")
        st.write(df['open.int.'].describe())  # Get descriptive statistics
        st.write("Open.Int. data type:", df['open.int.'].dtype)
        st.write("Unique values in Open.Int.:", df['open.int.'].unique())
        st.write("Non-finite values:", df[~np.isfinite(df['open.int.'])])

        fig = px.scatter_3d(df, x="Strike", y="gamma", z="implvol", size="open.int.", color="Strike", title="3D Plot (Gamma, Implied Volatility, Open Interest)")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating 3D plot: {e}")

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from io import StringIO

st.set_page_config(layout="wide")
st.title("📊 Options Data Dashboard")

# Function to calculate Gamma Flip
def calculate_gamma_flip(df):
    """
    Calculates the Gamma Flip point, handling potential edge cases.

    Args:
        df (pd.DataFrame): DataFrame with 'Strike' and 'gamma' columns.

    Returns:
        float: The strike price where Gamma flips, or None if not found.
    """
    if 'strike' not in df.columns or 'gamma' not in df.columns:
        return None  # Handle missing columns
    
    df_sorted = df.sort_values(by='strike')
    gamma_values = df_sorted['gamma'].values
    strike_values = df_sorted['strike'].values

    # Find the first index where Gamma changes sign
    flip_index = np.where(np.diff(np.sign(gamma_values)))[0]
    if len(flip_index) > 0:
        # Get the strike value at the flip index
        return strike_values[flip_index[0]]
    else:
        return None

# Function to create ThinkScript overlay
def create_thinkscript_overlay(gamma_flip, put_wall, call_wall):
    """
    Generates a ThinkScript overlay for key levels.

    Args:
        gamma_flip (float): Gamma Flip strike price.
        put_wall (float): Put Wall strike price.
        call_wall (float): Call Wall strike price.

    Returns:
        str: ThinkScript code for the overlay.
    """
    thinkscript = """
plot GammaFlip = %s;
GammaFlip.SetDefaultColor(Color.YELLOW);
plot PutWall = %s;
PutWall.SetDefaultColor(Color.RED);
plot CallWall = %s;
CallWall.SetDefaultColor(Color.GREEN);
    """ % (gamma_flip, put_wall, call_wall)
    return thinkscript

# Function to export Gamma key levels as CSV
def export_gamma_levels_csv(gamma_flip, put_wall, call_wall):
    """
    Generates a CSV string of Gamma key levels.

    Args:
        gamma_flip (float): Gamma Flip strike price.
        put_wall (float): Put Wall strike price.
        call_wall (float): Call Wall strike price.

    Returns:
        str: CSV formatted string.
    """
    data = {
        'Level': ['Gamma Flip', 'Put Wall', 'Call Wall'],
        'Strike': [gamma_flip, put_wall, call_wall]
    }
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

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
    try:
        df_raw = pd.read_excel(uploaded_file, header=1)  # Header starts from row 2 (index 1)
        return df_raw
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None  # Return None to indicate failure

# Streamlit Upload section
uploaded_file = st.file_uploader("Upload Options Chain Excel File (.xlsx)", type=["xlsx"])

if uploaded_file:
    # Load and clean data
    df = load_data(uploaded_file)
    if df is None:
        st.stop()  # Stop if loading failed

    # Clean specific columns
    df = clean_column(df, "Gamma")
    df = clean_column(df, "Impl Vol")
    df = clean_column(df, "Strike")  # Ensure no NaN values

    # 1. Print the actual column names in the DataFrame
    st.write("Actual DataFrame Columns:")
    st.write(df.columns.tolist())

     # 2. Normalize column names (lowercase and remove spaces) for comparison and to handle variations
    df.columns = df.columns.str.lower().str.replace(' ', '')
    
    # 3. Define the columns we want to keep (normalized)
    required_columns = ['gamma', 'implvol', 'strike']  # Added 'strike' and 'expiration'


    # 4. Ensure that the required columns are present *before* proceeding.
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Required column '{col}' not found.  Please check the column names in your Excel file.")
            st.stop()

    # Filter Calls and Puts Data (assuming data for calls is on the left of Strike and puts on the right)
    calls_data = df[df['strike'] <= df['strike'].max() // 2].copy()  # Use .copy() to avoid SettingWithCopyWarning
    puts_data = df[df['strike'] > df['strike'].max() // 2].copy()

    # Gamma Exposure for Calls
    st.subheader("📈 Gamma Exposure by Strike (Calls)")
    try:
        fig_calls = px.line(calls_data, x='strike', y='gamma', title="Gamma Exposure by Strike (Calls)")
        st.plotly_chart(fig_calls)
    except Exception as e:
        st.error(f"Error generating Gamma Exposure plot for Calls: {e}")

    # Gamma Exposure for Puts
    st.subheader("📈 Gamma Exposure by Strike (Puts)")
    try:
        fig_puts = px.line(puts_data, x='strike', y='gamma', title="Gamma Exposure by Strike (Puts)")
        st.plotly_chart(fig_puts)
    except Exception as e:
        st.error(f"Error generating Gamma Exposure plot for Puts: {e}")

    # 3D Scatter Plot - Gamma vs. Strike vs. Implied Volatility for Calls
    st.subheader("📉 3D Visualization of Calls")
    try:
        fig_calls_4d = px.scatter_3d(calls_data, x='strike', y='gamma', z='implvol', color='implvol',
                                     title="3D Visualization of Calls")
        st.plotly_chart(fig_calls_4d)
    except Exception as e:
        st.error(f"Error generating 3D plot for Calls: {e}")

    # 3D Scatter Plot - Gamma vs. Strike vs. Implied Volatility for Puts
    st.subheader("📉 3D Visualization of Puts")
    try:
        fig_puts_4d = px.scatter_3d(puts_data, x='strike', y='gamma', z='implvol', color='implvol',
                                     title="3D Visualization of Puts")
        st.plotly_chart(fig_puts_4d)
    except Exception as e:
        st.error(f"Error generating 3D plot for Puts: {e}")

    # 5D Visualization - Plotting the additional dimensions based on your requirements
    # Assuming you have 'Volume' and 'Delta' in your DataFrame
    if 'volume' in df.columns.str.lower() and 'delta' in df.columns.str.lower():
        calls_data['volume'] = df['volume']
        calls_data['delta'] = df['delta']
        puts_data['volume'] = df['volume']
        puts_data['delta'] = df['delta']
        
        st.subheader("🧮 5D Visualization of Calls")
        try:
            fig_calls_5d = px.scatter_3d(calls_data, x='strike', y='gamma', z='implvol', color='implvol',
                                         size='volume', symbol='delta', title="5D Visualization of Calls")
            st.plotly_chart(fig_calls_5d)
        except Exception as e:
            st.error(f"Error generating 5D plot for Calls: {e}")

        st.subheader("🧮 5D Visualization of Puts")
        try:
            fig_puts_5d = px.scatter_3d(puts_data, x='strike', y='gamma', z='implvol', color='implvol',
                                         size='volume', symbol='delta', title="5D Visualization of Puts")
            st.plotly_chart(fig_puts_5d)
        except Exception as e:
            st.error(f"Error generating 5D plot for Puts: {e}")
    else:
        st.warning("Columns 'Volume' or 'Delta' are missing. 5D visualization is not available.")

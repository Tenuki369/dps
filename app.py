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
    df_sorted = df.sort_values(by='Strike')
    gamma_values = df_sorted['gamma'].values
    strike_values = df_sorted['Strike'].values

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

# Upload file
uploaded_file = st.file_uploader("Upload Options Chain Excel File (.xlsx)", type="xlsx")

if uploaded_file:
    # Read the raw data
    df_raw = pd.read_excel(uploaded_file, header=None)
    st.subheader("📄 Raw Preview")
    st.write("First 20 Rows (no headers):")
    st.dataframe(df_raw.head(20))

    # Read the header row
    try:
        df_header = pd.read_excel(uploaded_file, header=1, nrows=1)
        st.write("Detected Column Names:")
        detected_columns = df_header.columns.tolist()  # Store detected column names
        st.write(detected_columns)
    except Exception as e:
        st.error(f"Failed to read headers from row 2: {e}")
        return

    # Load the data with headers set at row 2
    df = pd.read_excel(uploaded_file, header=1)
    st.subheader("📊 Cleaned Data Preview")

    # 1. Print the actual column names in the DataFrame
    st.write("Actual DataFrame Columns:")
    st.write(df.columns.tolist())

    # 2. Normalize column names (lowercase and remove spaces) for comparison and to handle variations
    df.columns = df.columns.str.lower().str.replace(' ', '')
    
    # 3. Define the columns we want to keep (normalized)
    required_columns = ['gamma', 'implvol', 'open.int.', 'strike', 'expiration']  # Added 'strike' and 'expiration'
    
    # 4. Drop rows with NaN in the required columns
    try:
        df = df.dropna(subset=required_columns)
    except KeyError as e:
        st.error(f"KeyError: {e}.  Please check the column names in your Excel file.  The application is expecting 'Gamma', 'Impl Vol', 'Open Int', 'Strike', and 'Expiration' (case-insensitive, spaces ignored).")
        return # Stop processing if there is a KeyError

    # 5. Ensure that the required columns are present *before* proceeding.
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Required column '{col}' not found.  Please check the column names in your Excel file.")
            return

    # Convert necessary columns to numeric, handling errors
    df['gamma'] = pd.to_numeric(df['gamma'], errors='coerce')
    df['implvol'] = pd.to_numeric(df['implvol'], errors='coerce')
    df['open.int.'] = pd.to_numeric(df['open.int.'], errors='coerce')
    df['strike'] = pd.to_numeric(df['strike'], errors='coerce')  # Convert 'Strike' to numeric


    # Replace any remaining NaN values after conversion
    df.fillna(0, inplace=True)

    # Display cleaned dataframe preview
    st.dataframe(df.head(20))

    # Gamma Exposure by Strike
    st.subheader("📈 Gamma Exposure by Strike")
    try:
        fig = px.scatter(df, x="strike", y="gamma", title="Gamma Exposure vs Strike")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating Gamma Exposure plot: {e}")

    # Implied Volatility Surface (3D)
    st.subheader("📉 Implied Volatility Surface")
    try:
        fig = px.scatter_3d(df, x="strike", y="expiration", z="implvol",
                           size="open.int.", color="strike",
                           title="Implied Volatility Surface (Strike, Expiration, Implied Volatility)")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating Implied Volatility Surface plot: {e}")

    # Gamma Flip Visualization
    st.subheader("🔄 Gamma Flip Visualization")
    try:
        gamma_flip = calculate_gamma_flip(df)  # Use the function
        if gamma_flip is not None:
            st.write(f"Gamma Flip is at Strike: {gamma_flip}")
        else:
            st.write("Gamma Flip not found.")
    except Exception as e:
        st.error(f"Error generating Gamma Flip visualization: {e}")

    # Placeholder values for Put Wall and Call Wall (replace with actual calculations)
    put_wall = 100  # Example value, replace with your calculation
    call_wall = 120  # Example value, replace with your calculation

    # Export ThinkOrSwim Script
    st.subheader("🚀 Export ThinkOrSwim Script")
    thinkscript_overlay = create_thinkscript_overlay(gamma_flip, put_wall, call_wall)
    st.text_area("ThinkScript Overlay", value=thinkscript_overlay, height=200)
    
    # Add a download button
    st.download_button(
        label="Download ThinkScript",
        data=thinkscript_overlay,
        file_name="gamma_overlay.ts",
        mime="text/plain",
    )

    # Export Gamma Key Levels as CSV
    st.subheader("📊 Gamma Key Levels (CSV)")
    gamma_levels_csv = export_gamma_levels_csv(gamma_flip, put_wall, call_wall)
    st.dataframe(pd.read_csv(StringIO(gamma_levels_csv)))  # Display as DataFrame
    st.download_button(
        label="Download Gamma Levels CSV",
        data=gamma_levels_csv,
        file_name="gamma_levels.csv",
        mime="text/csv",
    )

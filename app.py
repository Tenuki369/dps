import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Function to clean the specified column by converting values to numeric, removing '%' symbols
def clean_column(df, column_name):
    df[column_name] = df[column_name].astype(str).str.replace('%', '').apply(pd.to_numeric, errors='coerce')
    return df

# Load and clean data
def load_data(file):
    # Read the file with header at row 1 (index 0)
    df = pd.read_excel(file, header=0)
    
    # Clean the necessary columns (converting data types and handling non-numeric characters)
    df = clean_column(df, "Gamma")      # Clean Gamma column
    df = clean_column(df, "Impl Vol")   # Clean Impl Vol column
    df = clean_column(df, "Open.Int")   # Clean Open.Int column
    df = clean_column(df, "Theta")      # Clean Theta column
    df = clean_column(df, "Delta")      # Clean Delta column
    df = clean_column(df, "Volume")     # Clean Volume column
    df = clean_column(df, "Vega")       # Clean Vega column
    df = clean_column(df, "BID")        # Clean BID column
    df = clean_column(df, "ASK")        # Clean ASK column
    df = clean_column(df, "Exp")        # Clean Exp column
    df = clean_column(df, "Strike")     # Clean Strike column

    # Replace 'N/A' with 0 in the entire dataframe
    df = df.replace('N/A', 0)

    # Handling Calls (data for calls is on the left side of Strike)
    calls = df.iloc[:, :11]  # Columns for calls (before the strike)
    
    # Handling Puts (data for puts is on the right side of Strike)
    puts = df.iloc[:, 11:]   # Columns for puts (after the strike)
    
    return calls, puts

# Visualize Gamma Exposure by Strike
def plot_gamma_exposure(calls, puts):
    # Plot for Calls
    fig_calls = px.line(calls, x='Strike', y='Gamma', title="Gamma Exposure by Strike (Calls)")
    st.plotly_chart(fig_calls)

    # Plot for Puts
    fig_puts = px.line(puts, x='Strike', y='Gamma', title="Gamma Exposure by Strike (Puts)")
    st.plotly_chart(fig_puts)

# Visualize Implied Volatility Surface
def plot_implied_volatility(calls, puts):
    fig = px.scatter_3d(calls, x='Strike', y='Gamma', z='Impl Vol', title="Implied Volatility Surface (Calls)")
    st.plotly_chart(fig)

    fig_puts = px.scatter_3d(puts, x='Strike', y='Gamma', z='Impl Vol', title="Implied Volatility Surface (Puts)")
    st.plotly_chart(fig_puts)

# Visualize Gamma Flip
def plot_gamma_flip(calls, strike_val=95):
    gamma_flip = calls[calls['Strike'] == strike_val]
    fig = px.scatter(gamma_flip, x='Strike', y='Gamma', title="Gamma Flip at Strike: " + str(strike_val))
    st.plotly_chart(fig)

# 3D Plotting for Gamma, Implied Volatility, and Open Int
def plot_3d(calls):
    fig = go.Figure(data=[go.Scatter3d(
        x=calls['Strike'],
        y=calls['Gamma'],
        z=calls['Impl Vol'],
        mode='markers',
        marker=dict(
            size=calls['Open.Int'],
            color=calls['Open.Int'],
            colorscale='Viridis',
            opacity=0.8
        )
    )])
    fig.update_layout(title="3D Gamma, Implied Volatility and Open Interest", scene=dict(
                    xaxis_title='Strike',
                    yaxis_title='Gamma',
                    zaxis_title='Impl Vol'))
    st.plotly_chart(fig)

# Streamlit App Interface
def main():
    st.title("Options Gamma Dashboard")

    # Upload Excel file
    uploaded_file = st.file_uploader("Upload Options Chain Excel File", type=["xlsx"])

    if uploaded_file is not None:
        # Load data
        calls_data, puts_data = load_data(uploaded_file)

        # Display data
        st.subheader("Raw Data")
        st.write(calls_data.head())

        # Plot Gamma Exposure by Strike
        st.subheader("Gamma Exposure by Strike")
        plot_gamma_exposure(calls_data, puts_data)

        # Plot Implied Volatility Surface
        st.subheader("Implied Volatility Surface")
        plot_implied_volatility(calls_data, puts_data)

        # Plot Gamma Flip (Can select strike)
        st.subheader("Gamma Flip Visualization")
        strike_val = st.slider("Select Strike Value for Gamma Flip", int(calls_data['Strike'].min()), int(calls_data['Strike'].max()), 95)
        plot_gamma_flip(calls_data, strike_val)

        # 3D Visualization
        st.subheader("Multi-Dimensional 3D Visualization")
        plot_3d(calls_data)

# Run Streamlit app
if __name__ == '__main__':
    main()

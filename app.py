import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📊 Options Gamma Dashboard")

uploaded_file = st.file_uploader("Upload Options Chain Excel File (.xlsx)", type="xlsx")

if uploaded_file:
    # Read headers from row 2 (index 1)
    df = pd.read_excel(uploaded_file, header=1)
    st.write("📄 Detected Columns:", df.columns.tolist())

    # Attempt to map and clean columns
    try:
        # Clean column names and handle missing columns
        df.columns = df.columns.str.strip()  # Remove extra spaces
        expected_columns = ["Gamma", "Impl Vol", "Open.Int", "Strike", "Expiration"]

        # Check if all expected columns exist
        for col in expected_columns:
            if col not in df.columns:
                st.error(f"⚠️ Column '{col}' is missing!")
                raise KeyError(f"Missing expected column: {col}")

        df = df[expected_columns]
        df.columns = ["Gamma", "ImpliedVol", "OpenInterest", "Strike", "Expiration"]

        # Clean the data: remove non-numeric values in numerical columns
        df["Strike"] = pd.to_numeric(df["Strike"], errors="coerce")
        df["Gamma"] = pd.to_numeric(df["Gamma"], errors="coerce")
        df["OpenInterest"] = pd.to_numeric(df["OpenInterest"], errors="coerce")
        df["ImpliedVol"] = df["ImpliedVol"].astype(str).str.replace('%', '')
        df["ImpliedVol"] = pd.to_numeric(df["ImpliedVol"], errors="coerce")
        df["Expiration"] = pd.to_datetime(df["Expiration"], errors="coerce")

        # Drop rows with missing values in essential columns
        df = df.dropna(subset=["Strike", "Gamma", "ImpliedVol", "Expiration"])
        st.write("✅ Cleaned Data Preview", df.head(20))

        # --- Gamma by Strike ---
        st.subheader("Gamma by Strike")
        gamma_by_strike = df.groupby("Strike")["Gamma"].sum().dropna().sort_index()
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.bar(gamma_by_strike.index, gamma_by_strike.values, color='steelblue')
        ax1.set_title("Net Gamma by Strike")
        ax1.set_xlabel("Strike")
        ax1.set_ylabel("Net Gamma")
        st.pyplot(fig1)

        # --- Gamma Flip ---
        gamma_flip = None
        for i in range(1, len(gamma_by_strike)):
            if gamma_by_strike.iloc[i - 1] < 0 and gamma_by_strike.iloc[i] > 0:
                x0, y0 = gamma_by_strike.index[i - 1], gamma_by_strike.iloc[i - 1]
                x1, y1 = gamma_by_strike.index[i], gamma_by_strike.iloc[i]
                gamma_flip = x0 - y0 * (x1 - x0) / (y1 - y0)
                break

        put_wall = gamma_by_strike.idxmin()
        call_wall = gamma_by_strike.idxmax()

        st.write("**Gamma Flip Zone:**", gamma_flip)
        st.write("**Put Wall:**", put_wall)
        st.write("**Call Wall:**", call_wall)

        # --- Volatility Surface (3D) ---
        st.subheader("Volatility Surface (3D)")
        pivot = df.pivot_table(index="Strike", columns="Expiration", values="ImpliedVol")
        X, Y = np.meshgrid(pivot.columns, pivot.index)
        Z = pivot.values

        fig2 = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
        fig2.update_layout(title='Implied Volatility Surface', scene=dict(
            xaxis_title='Expiration',
            yaxis_title='Strike',
            zaxis_title='Implied Vol (%)'
        ))
        st.plotly_chart(fig2, use_container_width=True)

        # --- Export Gamma Levels ---
        st.subheader("Export Gamma Key Levels")
        input_line = f"input gammaFlip = {gamma_flip:.2f};" if gamma_flip is not None else ""
        plot_line = """plot GammaFlip = gammaFlip;
GammaFlip.SetStyle(Curve.SHORT_DASH);
GammaFlip.SetDefaultColor(Color.YELLOW);
""" if gamma_flip is not None else ""

        output = f"""
# === GOOGL Gamma Overlay ===
input putWall = {put_wall};
input callWall = {call_wall};
{input_line}

plot PutWall = putWall;
PutWall.SetStyle(Curve.LONG_DASH);
PutWall.SetDefaultColor(Color.RED);

plot CallWall = callWall;
CallWall.SetStyle(Curve.LONG_DASH);
CallWall.SetDefaultColor(Color.GREEN);

{plot_line}
"""

        st.download_button("📥 Download ThinkScript", output, file_name="GOOGL_GammaOverlay.txt")

        gamma_csv = pd.DataFrame({
            "Level": ["Gamma Flip", "Put Wall", "Call Wall"],
            "Strike": [gamma_flip, put_wall, call_wall]
        })
        csv = gamma_csv.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, file_name="GOOGL_GammaLevels.csv", mime="text/csv")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

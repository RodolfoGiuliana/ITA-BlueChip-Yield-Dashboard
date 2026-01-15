import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Simulatore Certificato Bancario", layout="wide")

# --- TITOLO E INFO CERTIFICATO ---
st.title("📊 Simulatore Certificato Investment")
st.markdown("---")

col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.metric("ISIN", "IT000X123456")
with col_info2:
    st.metric("EMITTENTE", "Binance / Simulation")
with col_info3:
    st.metric("SCADENZA", "15/01/2027")

# --- PARAMETRI DEL CERTIFICATO ---
st.sidebar.header("Parametri del Certificato")
barrier_level = st.sidebar.slider("Livello Barriera (%)", 50, 80, 60)
strike_date = st.sidebar.date_input("Data di Strike", datetime(2024, 1, 1))

# Mapping Ticker
tickers = {
    "GENERALI": "G.MI",
    "TENARIS": "TEN.MI",
    "TERNA": "TRN.MI"
}

# --- DOWNLOAD DATI ---
@st.cache_data
def load_data(symbols):
    data = yf.download(list(symbols.values()), start="2024-01-01")['Close']
    return data

data = load_data(tickers)

# --- ANALISI PERFORMANCE ---
st.subheader("Analisi Sottostanti (Worst Of)")

cols = st.columns(3)
perf_data = {}

for i, (name, ticker) in enumerate(tickers.items()):
    with cols[i]:
        # Calcolo Performance
        strike_price = data[ticker].iloc[0]
        current_price = data[ticker].iloc[-1]
        perf = ((current_price - strike_price) / strike_price) * 100
        
        # UI Card
        st.markdown(f"### {name}")
        st.write(f"Prezzo Strike: **€{strike_price:.2f}**")
        st.write(f"Prezzo Attuale: **€{current_price:.2f}**")
        st.metric("Performance", f"{perf:.2f}%", delta=f"{perf:.2f}%")
        
        # Stato Barriera
        dist_barriera = perf + (100 - barrier_level)
        if current_price < (strike_price * (barrier_level/100)):
            st.error("⚠️ SOTTO BARRIERA")
        else:
            st.success(f"Distanza Barriera: {dist_barriera:.2f}%")
        
        perf_data[name] = perf

# --- GRAFICO COMPARATIVO ---
st.markdown("---")
st.subheader("Andamento Storico Sottostanti (Normalizzato a 100)")

# Normalizzazione dei dati per confronto
norm_data = (data / data.iloc[0]) * 100
fig = go.Figure()

for name, ticker in tickers.items():
    fig.add_trace(go.Scatter(x=norm_data.index, y=norm_data[ticker], name=name))

# Linea Barriera (approssimativa sul grafico)
fig.add_hline(y=barrier_level, line_dash="dash", line_color="red", annotation_text="Livello Barriera")

fig.update_layout(template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

# --- LOGICA DEL "WORST OF" ---
worst_stock = min(perf_data, key=perf_data.get)
st.info(f"Il titolo peggiore (Worst-of) al momento è: **{worst_stock}** con una performance del {perf_data[worst_stock]:.2f}%")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Investment Certificate Pro", layout="wide")

# --- HEADER E INFO CERTIFICATO ---
st.title("🏛️ Simulatore Multi-Asset per Certificati")
st.markdown("Creato da Rodolfo Giuliana - Analisi interattiva su paniere Generali, Tenaris e Terna.")

st.sidebar.header("⚙️ Parametri del Certificato")
barrier_level = st.sidebar.slider("Livello Barriera (%)", 50, 80, 60)
notional = st.sidebar.number_input("Capitale Investito (€)", value=1000)
strike_date = "2024-01-01"

# Dati tecnici fittizi
col_i1, col_i2, col_i3, col_i4 = st.columns(4)
with col_i1: st.metric("ISIN", "IT000X123456")
with col_i2: st.metric("SOTTOSTANTI", "3 Blue Chips")
with col_i3: st.metric("BARRIERA", f"{barrier_level}%")
with col_i4: st.metric("VALUTA", "EUR")

# --- DOWNLOAD DATI ---
tickers = {"GENERALI": "G.MI", "TENARIS": "TEN.MI", "TERNA": "TRN.MI"}

@st.cache_data
def get_market_data(symbols):
    df = yf.download(list(symbols.values()), start=strike_date)['Close']
    return df

# --- BLOCCO PRINCIPALE ---
data = get_market_data(tickers)

if data.empty:
    st.error("Errore nel caricamento dei dati da Yahoo Finance.")
else:
    # --- ANALISI PERFORMANCE SOTTOSTANTI ---
    st.header("📈 Analisi Real-Time Sottostanti")
    cols = st.columns(3)
    perf_data = {}

    for i, (name, ticker) in enumerate(tickers.items()):
        with cols[i]:
            strike_price = data[ticker].iloc[0]
            current_price = data[ticker].iloc[-1]
            perf = ((current_price - strike_price) / strike_price) * 100
            perf_data[name] = perf
            
            st.markdown(f"### {name}")
            st.metric("Performance", f"{perf:.2f}%", delta=f"{(current_price - strike_price):.2f}€")
            
            barriera_val = strike_price * (barrier_level / 100)
            if current_price < barriera_val:
                st.error(f"⚠️ SOTTO BARRIERA ({barriera_val:.2f})")
            else:
                st.success(f"Sopra Barriera")

    worst_stock_name = min(perf_data, key=perf_data.get)
    worst_ticker = tickers[worst_stock_name]

    # --- GRAFICO PERFORMANCE ---
    norm_data = (data / data.iloc[0]) * 100
    fig_perf = go.Figure()
    for name, ticker in tickers.items():
        fig_perf.add_trace(go.Scatter(x=norm_data.index, y=norm_data[ticker], name=name))
    fig_perf.add_hline(y=barrier_level, line_dash="dash", line_color="red")
    fig_perf.update_layout(title="Andamento Sottostanti (Base 100)", template="plotly_dark")
    st.plotly_chart(fig_perf, use_container_width=True)

    # --- ANALISI QUANTITATIVA ---
    st.markdown("---")
    st.header("🔬 Analisi Quantitativa ed Emittente")
    
    col_q1, col_q2 = st.columns([1, 2])
    
    with col_q1:
        st.subheader("Correlazione")
        corr = data.pct_change().corr()
        try:
            st.dataframe(corr.style.format("{:.2f}").background_gradient(cmap='Greens', axis=None))
        except:
            st.dataframe(corr.style.format("{:.2f}"))

    with col_q2:
        st.subheader(f"Monte Carlo: {worst_stock_name}")
        sims, t_days = 1000, 252
        returns = data[worst_ticker].pct_change().dropna()
        mu, sigma = returns.mean(), returns.std()
        last_p = data[worst_ticker].iloc[-1]
        
        simulation_df = pd.DataFrame()
        for i in range(sims):
            daily_rets = np.random.normal(mu, sigma, t_days)
            simulation_df[i] = last_p * (1 + daily_rets).cumprod()
        
        fig_mc = go.Figure()
        for i in range(30):
            fig_mc.add_trace(go.Scatter(y=simulation_df[i], mode='lines', line=dict(width=0.5), opacity=0.3, showlegend=False))
        st.plotly_chart(fig_mc, use_container_width=True)

    # --- PAYOFF ---
    st.markdown("---")
    st.subheader("Profilo di Rimborso a Scadenza")
    p_range = np.linspace(-100, 40, 100)
    payoff = [notional if p > (barrier_level - 100) else notional * (1 + p/100) for p in p_range]
    fig_payoff = go.Figure(go.Scatter(x=p_range, y=payoff, fill='tozeroy'))
    fig_payoff.update_layout(xaxis_title="Perf Worst-Of (%)", yaxis_title="Rimborso (€)", template="plotly_dark")
    st.plotly_chart(fig_payoff, use_container_width=True)

st.caption("⚠️ Simulazione a scopo didattico.")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Investment Certificate Pro", layout="wide")

# --- HEADER E INFO CERTIFICATO ---
st.title("🏛️ Term Sheet Simulator: Multi-Asset Certificate")
st.markdown("""
Creato da Rodolfo Giuliana Questo framework simula un certificato di investimento **Cash Collect Worst-Of**. 
Analizza la probabilità di protezione del capitale attraverso simulazioni stocastiche.
""")

st.sidebar.header("⚙️ Parametri del Certificato")
barrier_level = st.sidebar.slider("Livello Barriera (%)", 50, 80, 60, help="Sotto questo livello il capitale non è protetto")
notional = st.sidebar.number_input("Capitale Investito (€)", value=1000)
strike_date = "2024-01-01"

# Dati tecnici
col_i1, col_i2, col_i3, col_i4 = st.columns(4)
with col_i1: st.metric("ISIN", "IT000X123456")
with col_i2: st.metric("SOTTOSTANTI", "3 Blue Chips")
with col_i3: st.metric("BARRIERA", f"{barrier_level}%")
with col_i4: st.metric("VALUTA", "EUR")

# --- DOWNLOAD DATI ---
tickers = {
    "GENERALI": "G.MI",
    "TENARIS": "TEN.MI",
    "TERNA": "TRN.MI"
}

@st.cache_data
def get_market_data(symbols):
    df = yf.download(list(symbols.values()), start=strike_date)['Close']
    return df

try:
            # Prova a visualizzare con i colori (richiede matplotlib)
            st.dataframe(corr.style.format("{:.2f}").background_gradient(cmap='Greens', axis=None))
    
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
            
            # Status Barriera
            barriera_val = strike_price * (barrier_level / 100)
            if current_price < barriera_val:
                st.error(f"⚠️ SOTTO BARRIERA (Target: {barriera_val:.2f})")
            else:
                st.success(f"Sopra Barriera (+{perf + (100-barrier_level):.1f}%)")

    # Identificazione Worst-Of
    worst_stock_name = min(perf_data, key=perf_data.get)
    worst_ticker = tickers[worst_stock_name]
    st.info(f"👉 Il titolo **Worst-Of** attuale è: **{worst_stock_name}**")

    # --- GRAFICO PERFORMANCE NORMALIZZATA ---
    norm_data = (data / data.iloc[0]) * 100
    fig_perf = go.Figure()
    for name, ticker in tickers.items():
        fig_perf.add_trace(go.Scatter(x=norm_data.index, y=norm_data[ticker], name=name))
    
    fig_perf.add_hline(y=barrier_level, line_dash="dash", line_color="red", annotation_text="Barriera Protezione")
    fig_perf.update_layout(title="Andamento Sottostanti (Base 100)", template="plotly_dark", height=450)
    st.plotly_chart(fig_perf, use_container_width=True)

    # --- QUANTITATIVE ANALYSIS SECTION ---
    st.markdown("---")
    st.header("🔬 Analisi Quantitativa per l'Emittente")
    
    col_q1, col_q2 = st.columns([1, 2])
    
   with col_q1:
        st.subheader("Matrice di Correlazione")
        # Calcolo correlazione log-returns
        corr = data.pct_change().corr()
        st.dataframe(corr.style.format("{:.2f}").background_gradient(cmap='Greens', axis=None))
        st.caption("Una correlazione bassa tra i titoli aumenta il premio (cedola) ma alza il rischio 'Worst-of'.")

    with col_q2:
        st.subheader(f"Monte Carlo: {worst_stock_name}")
        
        # Parametri simulazione
        sims = 1000
        t_days = 252
        returns = data[worst_ticker].pct_change().dropna()
        mu = returns.mean()
        sigma = returns.std()
        last_p = data[worst_ticker].iloc[-1]
        
        # Generazione scenari (Geometric Brownian Motion)
        simulation_df = pd.DataFrame()
        for i in range(sims):
            daily_rets = np.random.normal(mu, sigma, t_days)
            price_path = last_p * (1 + daily_rets).cumprod()
            simulation_df[i] = price_path
        
        # Plot Monte Carlo
        fig_mc = go.Figure()
        for i in range(40): # Mostriamo solo 40 traiettorie
            fig_mc.add_trace(go.Scatter(y=simulation_df[i], mode='lines', line=dict(width=0.5), opacity=0.3, showlegend=False))
        
        # Linea barriera (in valore assoluto)
        b_val_abs = data[worst_ticker].iloc[0] * (barrier_level / 100)
        fig_mc.add_hline(y=b_val_abs, line_dash="dot", line_color="red")
        fig_mc.update_layout(title="1.000 Scenari Futuri (1 anno)", template="plotly_dark", height=400)
        st.plotly_chart(fig_mc, use_container_width=True)

    # --- KPI DI RISCHIO ---
    st.subheader("Indicatori di Probabilità")
    final_prices = simulation_df.iloc[-1]
    prob_success = (final_prices > b_val_abs).sum() / sims * 100
    vol_annua = sigma * np.sqrt(252) * 100

    col_k1, col_k2, col_k3 = st.columns(3)
    col_k1.metric("Probabilità Protezione Capitale", f"{prob_success:.1f}%")
    col_k2.metric("Volatilità Realizzata (Worst-of)", f"{vol_annua:.2f}%")
    col_k3.metric("Distanza Barriera (Worst-of)", f"{perf_data[worst_stock_name] + (100-barrier_level):.2f}%")

    # --- PAYOFF CHART ---
    st.markdown("---")
    st.subheader("Profilo di Rimborso a Scadenza")
    
    # Calcolo payoff lineare sotto barriera
    p_range = np.linspace(-100, 40, 100)
    payoff = [notional if p > (barrier_level - 100) else notional * (1 + p/100) for p in p_range]
    
    fig_payoff = go.Figure()
    fig_payoff.add_trace(go.Scatter(x=p_range, y=payoff, fill='tozeroy', name="Rimborso (€)"))
    fig_payoff.update_layout(
        title="Payoff stimato basato sulla performance del titolo peggiore",
        xaxis_title="Performance Worst-Of (%)",
        yaxis_title="Valore di Rimborso (€)",
        template="plotly_dark"
    )
    st.plotly_chart(fig_payoff, use_container_width=True)

except ImportError:
            # Se matplotlib manca ancora, mostra la tabella semplice
            st.dataframe(corr.style.format("{:.2f}"))
            st.warning("Nota: Installa 'matplotlib' per vedere i colori nella tabella.")
            
        st.caption("Una correlazione bassa tra i titoli aumenta il premio (cedola) ma alza il rischio 'Worst-of'.")
st.markdown("---")
st.caption("⚠️ Disclaimer: Questa è una simulazione a scopo didattico. Non costituisce consulenza finanziaria.")

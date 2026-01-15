import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="Simulatore Certificato Bancario", layout="wide")

# --- TITOLO E INFO CERTIFICATO ---
st.title("📊 Simulatore Certificato Investment")
st.markdown("Creato da Rodolfo Giuliana")

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




import numpy as np

st.markdown("---")
st.header("🔬 Analisi Quantitativa per l'Emittente")

# --- 1. MATRICE DI CORRELAZIONE ---
st.subheader("Matrice di Correlazione dei Sottostanti")
st.write("Un'alta correlazione riduce il rischio del paniere 'Worst-of'.")
correlation_matrix = data.pct_change().corr()
st.dataframe(correlation_matrix.style.background_gradient(cmap='RdYlGn'))

# --- 2. SIMULAZIONE MONTE CARLO ---
st.subheader(f"Simulazione Monte Carlo: {worst_stock} (Worst-of)")

# Parametri Simulazione
days_to_expiry = 252 # Simuliamo 1 anno di trading
simulations = 1000

# Calcolo rendimenti e volatilità
returns = data[tickers[worst_stock]].pct_change()
mu = returns.mean()
sigma = returns.std()
last_price = data[tickers[worst_stock]].iloc[-1]

# Generazione Scenari
simulation_df = pd.DataFrame()
for i in range(simulations):
    daily_returns = np.random.normal(mu, sigma, days_to_expiry)
    price_path = last_price * (1 + daily_returns).cumprod()
    simulation_df[i] = price_path

# Visualizzazione Proiezioni
fig_mc = go.Figure()
for i in range(50): # Mostriamo solo 50 linee per non appesantire
    fig_mc.add_trace(go.Scatter(y=simulation_df[i], mode='lines', 
                               line=dict(width=1), opacity=0.3, showlegend=False))

# Linea Barriera in Monte Carlo
barrier_price = data[tickers[worst_stock]].iloc[0] * (barrier_level / 100)
fig_mc.add_hline(y=barrier_price, line_dash="dash", line_color="red", annotation_text="Barriera")
fig_mc.update_layout(title=f"1.000 Scenari futuri per {worst_stock}", template="plotly_dark")
st.plotly_chart(fig_mc, use_container_width=True)

# --- 3. PROBABILITÀ DI SUCCESSO ---
final_prices = simulation_df.iloc[-1]
prob_above_barrier = (final_prices > barrier_price




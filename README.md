# 📊 Multi-Asset Investment Certificate Simulator

Questo progetto è un framework interattivo sviluppato da Rodolfo Giuliana in **Streamlit** per l'analisi e il monitoraggio di un certificato d'investimento strutturato (simulazione) sui titoli **Generali (G.MI)**, **Tenaris (TEN.MI)** e **Terna (TRN.MI)**.

## 🚀 Funzionalità principali
* **Real-time Data Fetching:** Integrazione con Yahoo Finance per prezzi aggiornati.
* **Worst-of Logic:** Calcolo automatico del titolo peggiore nel paniere per determinare la tenuta della barriera.
* **Visualizzazione Dinamica:** Grafici interattivi con Plotly per confrontare le performance normalizzate (Base 100).
* **Simulatore di Parametri:** Possibilità di modificare il livello della barriera e la data di strike tramite sidebar.

## 🛠️ Tech Stack
* **Python 3.9+**
* **Streamlit** (Web UI)
* **Pandas/YFinance** (Data Processing)
* **Plotly** (Visualizzazione Grafica)

## 📋 Come eseguire il progetto localmente
1. Clona il repository: `git clone https://github.com/TUO-USERNAME/NOME-REPO.git`
2. Installa le dipendenze: `pip install -r requirements.txt`
3. Avvia l'app: `streamlit run app.py`

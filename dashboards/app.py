"""
Dashboard d'analyse financière -Plateforme de scoring et allocation d'actifs

Ce dashboard permet de :
- Visualiser les KPIs financiers
- Classer les actifs selon un score composite
- Comparer le risque et le rendement

Technologies :
- Streamlit
- Plotly
- Pandas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# Configuration générale
st.set_page_config(
    page_title="Analyse Financière",
    layout="wide"
)

# Chargement du CSS
def load_css():
    css_path = Path("dashboards/assets/style.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Chargement des données Gold
DATA_PATH = Path("storage/data/gold/asset_scores.parquet")
df = pd.read_parquet(DATA_PATH)

# Chargement allocation optimale
ALLOC_PATH = Path("storage/data/gold/portfolio_allocation.parquet")
allocation = pd.read_parquet(ALLOC_PATH)

# Sidebar
st.sidebar.title("📊 Paramètres")
selected_assets = st.sidebar.multiselect(
    "Sélection des actifs",
    options=df["ticker"].unique(),
    default=df["ticker"].head(5).tolist()
)

df_filtered = df[df["ticker"].isin(selected_assets)]

# Titre principal
st.title("📈 Plateforme d'analyse financière")
st.markdown(
    "Analyse de la **performance ajustée du risque** des actifs financiers."
)

# KPIs globaux
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Sharpe moyen", f"{df_filtered['sharpe_ratio'].mean():.2f}")

with col2:
    st.metric("Rendement moyen annuel", f"{df_filtered['annual_return'].mean():.2%}")

with col3:
    st.metric("Volatilité moyenne", f"{df_filtered['volatility'].mean():.2%}")

# Classement des actifs
st.subheader("🏆 Classement des actifs par score")

ranking = df_filtered.sort_values("score", ascending=False)
st.dataframe(
    ranking[["ticker", "score", "sharpe_ratio", "annual_return", "volatility", "max_drawdown"]],
    use_container_width=True
)

# Graphique Risque / Rendement
st.subheader("📉 Risque vs Rendement")

fig_rr = px.scatter(
    ranking,
    x="volatility",
    y="annual_return",
    size="score",
    color="ticker",
    hover_name="ticker",
    labels={
        "volatility": "Volatilité annualisée",
        "annual_return": "Rendement annualisé"
    }
)

st.plotly_chart(fig_rr, use_container_width=True)

# Graphique Sharpe Ratio
st.subheader("📊 Sharpe Ratio par actif")

fig_sharpe = px.bar(
    ranking,
    x="ticker",
    y="sharpe_ratio",
    color="ticker",
    labels={"sharpe_ratio": "Sharpe Ratio"}
)

st.plotly_chart(fig_sharpe, use_container_width=True)


# Chargement des rendements Silver
RETURNS_PATH = Path("storage/data/silver/prices_clean.parquet")
df_returns = pd.read_parquet(RETURNS_PATH)

returns_pivot = (
    df_returns
    .pivot(index="Date", columns="ticker", values="return")
    .fillna(0)
)

st.markdown("---")
st.subheader("📐 Allocation optimale du portefeuille (Markowitz)")

# --- SÉCURISATION DU CHARGEMENT ---
try:
    # 1. Aligner les tickers entre les rendements et l'allocation
    # On ne garde que les tickers communs aux deux fichiers
    common_tickers = list(set(returns_pivot.columns) & set(allocation["ticker"]))
    
    if not common_tickers:
        st.error("Aucun ticker commun trouvé entre les prix et l'allocation.")
    else:
        # Filtrer et réordonner pour que l'ordre des colonnes == l'ordre des poids
        returns_pivot_filtered = returns_pivot[common_tickers]
        alloc_filtered = allocation.set_index("ticker").loc[common_tickers]
        weights = alloc_filtered["weight"].values

        # Affichage du camembert (Pie Chart)
        fig_alloc = px.pie(
            alloc_filtered.reset_index(), 
            names="ticker", 
            values="weight", 
            title="Répartition optimale du portefeuille",
            hole=0.4
        )
        st.plotly_chart(fig_alloc, use_container_width=True)


        # 2. Calculs Rendement & Volatilité
        avg_returns = returns_pivot_filtered.mean() * 252
        portfolio_return = np.dot(avg_returns, weights)

        # Calcul matriciel robuste pour la volatilité
        cov_matrix = returns_pivot_filtered.cov() * 252
        portfolio_volatility = (weights.T @ cov_matrix @ weights) ** 0.5
      

        # Affichage des métriques
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rendement annuel portefeuille", f"{portfolio_return:.2%}")
        with col2:
            st.metric("Volatilité annuelle portefeuille", f"{portfolio_volatility:.2%}")

        # 3. Comparaison Équipondéré
        n_assets = len(common_tickers)
        equal_weights = [1 / n_assets] * n_assets
        ew_return = (returns_pivot_filtered.mean() * 252) @ equal_weights
        ew_volatility = (np.array(equal_weights).T @ cov_matrix @ np.array(equal_weights)) ** 0.5

        #st.write("DEBUG - Poids Markowitz :", weights)
        #st.write("DEBUG - Poids Équipondérés :", equal_weights)

        comparison = pd.DataFrame({
            "Portefeuille": ["Équipondéré", "Optimal (Markowitz)"],
            "Rendement annuel": [ew_return, portfolio_return],
            "Volatilité annuelle": [ew_volatility, portfolio_volatility]
        })
        
        st.subheader("🔍 Comparaison des portefeuilles")
        st.table(comparison.style.format({
            "Rendement annuel": "{:.2%}",
            "Volatilité annuelle": "{:.2%}"
        }))

except Exception as e:
    st.error(f"Erreur lors du calcul du portefeuille : {e}")

st.info(
    "L’allocation optimale est calculée selon la théorie moderne du portefeuille "
    "(Markowitz) en minimisant la volatilité sous contrainte de diversification "
    "(pas de vente à découvert, somme des poids = 1)."
)

# Footer
st.markdown("---")
st.markdown(
    " **Projet personnel - Finance de marché & Data Engineering**"
)
"""
Module de scoring multi-critères des actifs financiers.

Objectif
--------
Calculer un score composite permettant de classer les actifs financiers
en fonction de leur performance ajustée du risque.

Le score est basé sur des indicateurs financiers classiques :
- Rendement annualisé
- Volatilité annualisée
- Sharpe Ratio
- Max Drawdown

Ce module correspond à la couche analytique métier (Gold).
"""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path

# Chemin vers les KPIs calculés en couche Gold
GOLD_KPIS_PATH = Path("storage/data/gold/asset_kpis.parquet")

# Chemin de sortie du scoring
GOLD_SCORE_PATH = Path("storage/data/gold/asset_scores.parquet")


def compute_asset_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule un score composite pour chaque actif financier.

    Méthodologie
    -------------
    1. Normalisation des indicateurs financiers entre 0 et 1
    2. Pondération des indicateurs selon leur importance métier
    3. Agrégation en un score unique

    Pondérations retenues
    ---------------------
    - Sharpe Ratio      : 40 %
    - Rendement         : 30 %
    - Volatilité        : 20 % (pénalisée)
    - Max Drawdown      : 10 % (pénalisé)

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame contenant les KPIs financiers par actif.

    Returns
    -------
    pandas.DataFrame
        DataFrame enrichi avec un score composite par actif.
    """

    scaler = MinMaxScaler()

    df_scaled = df.copy()

    # Indicateurs à maximiser
    df_scaled[["sharpe_ratio", "annual_return"]] = scaler.fit_transform(
        df[["sharpe_ratio", "annual_return"]]
    )

    # Indicateurs à minimiser (on inverse le signe avant normalisation)
    df_scaled[["volatility", "max_drawdown"]] = scaler.fit_transform(
        -df[["volatility", "max_drawdown"]]
    )

    # Calcul du score composite
    df["score"] = (
        0.4 * df_scaled["sharpe_ratio"] +
        0.3 * df_scaled["annual_return"] +
        0.2 * df_scaled["volatility"] +
        0.1 * df_scaled["max_drawdown"]
    )

    return df.sort_values("score", ascending=False)


if __name__ == "__main__":
    # Chargement des KPIs financiers
    df_kpis = pd.read_parquet(GOLD_KPIS_PATH)

    # Calcul du scoring
    df_scores = compute_asset_score(df_kpis)

    # Sauvegarde du résultat
    df_scores.to_parquet(GOLD_SCORE_PATH)

    print("✅ Scoring des actifs financiers terminé")
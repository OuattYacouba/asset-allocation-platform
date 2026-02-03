## 🟡 Couche Gold – KPIs financiers & Scoring

La couche Gold contient les indicateurs financiers à forte valeur métier,
destinés à l’aide à la décision et à la visualisation.

---

## 📈 Méthodologie des KPIs (Couche Gold)

Les indicateurs financiers sont calculés à partir des données de prix clôture nettoyées, en utilisant une base de **252 jours de trading** par an.

| KPI | Formule | Description |
| :--- | :--- | :--- |
| **Annual Return** | `AVG(returns) * 252` | Performance moyenne linéarisée sur un an. |
| **Volatility** | `STDDEV(returns) * √252` | Risque historique (écart-type). Plus elle est haute, plus l'actif est instable. |
| **Sharpe Ratio** | `Return / Volatility` | Rendement par unité de risque. Un ratio > 1 est considéré comme satisfaisant. |
| **Max Drawdown** | `Min(Value / Peak - 1)` | La plus forte baisse historique subie. Mesure le risque de perte extrême. |
| **N_Obs** | `Count(*)` | Nombre de jours traités, garantissant la validité statistique du calcul. |

> [!TIP]
> Pour le **Max Drawdown**, nous utilisons le rendement logarithmique pour reconstruire la courbe de performance cumulée et identifier les sommets successifs (*peaks*).

### Indicateurs calculés
- Rendement annualisé
- Volatilité annualisée
- Sharpe Ratio
- Max Drawdown
- Nombre d’observations

### Méthodologie de scoring
Un score composite est calculé pour chaque actif afin de permettre
un classement basé sur la performance ajustée du risque.

Pondérations retenues :
- Sharpe Ratio : 40 %
- Rendement : 30 %
- Volatilité : 20 % (pénalisée)
- Max Drawdown : 10 % (pénalisé)

Cette approche permet de favoriser les actifs performants,
stables et présentant un risque maîtrisé.


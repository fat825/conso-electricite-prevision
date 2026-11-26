from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).resolve().parent.parent / "models"
modele = joblib.load(DOSSIER / "modele_lineaire.joblib")
historique = pd.read_csv(DOSSIER / "conso_jour.csv", parse_dates=["date"])

VARIABLES = ["conso_hier", "conso_7j", "jour_semaine"]


def prevoir(nb_jours):
    valeurs = list(historique["conso_moyenne"])
    derniere_date = historique["date"].iloc[-1]
    resultats = []
    for i in range(1, nb_jours + 1):
        date = derniere_date + pd.Timedelta(days=i)
        ligne = pd.DataFrame([{
            "conso_hier": valeurs[-1],
            "conso_7j": valeurs[-7],
            "jour_semaine": date.dayofweek,
        }])
        pred = modele.predict(ligne[VARIABLES])[0]
        valeurs.append(pred)
        resultats.append({"date": date, "prevision": pred})
    return pd.DataFrame(resultats)


st.set_page_config(page_title="Prévision de consommation", page_icon="⚡")
st.title("⚡ Prévision de la consommation électrique (France)")
st.write(
    "Prévision de la consommation moyenne journalière à partir des données RTE. "
    "Plus l'horizon est lointain, moins la prévision est fiable."
)

nb_jours = st.slider("Nombre de jours à prévoir", 1, 7, 7)
prev = prevoir(nb_jours)

courbe = pd.concat([
    historique.set_index("date")["conso_moyenne"].rename("Historique"),
    prev.set_index("date")["prevision"].rename("Prévision"),
], axis=1)

st.line_chart(courbe.tail(40))
st.dataframe(prev.assign(prevision=prev["prevision"].round()))

st.caption(
    "Limites : modèle entraîné sur environ 3 mois seulement, sans jours fériés "
    "ni température. Erreur de 2 195 MW à 1 jour, bien plus à 7 jours."
)
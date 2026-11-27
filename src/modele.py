import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

VARIABLES = ["conso_hier", "conso_7j", "jour_semaine"]


def separer(tableau, nb_jours_test=17):
    """Coupe dans l'ordre du temps : le test vient après l'entraînement."""
    coupure = len(tableau) - nb_jours_test
    return tableau.iloc[:coupure], tableau.iloc[coupure:]


def entrainer(train):
    """Entraîne la régression linéaire."""
    modele = LinearRegression()
    modele.fit(train[VARIABLES], train["conso_moyenne"])
    return modele


def erreur(modele, test):
    """Erreur moyenne absolue (MW) sur le test."""
    predictions = modele.predict(test[VARIABLES])
    return mean_absolute_error(test["conso_moyenne"], predictions)


def prevoir(modele, historique, nb_jours=7):
    """Prévision récursive : chaque prédiction devient le 'hier' suivant."""
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


if __name__ == "__main__":
    from donnees import preparer

    tableau = preparer("data/eco2mix-national-tr.csv")
    train, test = separer(tableau)
    modele = entrainer(train)
    print("Lignes train / test :", len(train), "/", len(test))
    print("Erreur du modèle :", round(erreur(modele, test)), "MW")
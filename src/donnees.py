import pandas as pd


def charger_donnees(chemin):
    """Lit le CSV RTE et convertit la colonne Date."""
    df = pd.read_csv(chemin, sep=";")
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def regrouper_par_jour(df):
    """Moyenne des mesures de chaque jour : une ligne par jour."""
    conso_jour = df.groupby("Date")["Consommation (MW)"].mean().reset_index()
    conso_jour.columns = ["date", "conso_moyenne"]
    return conso_jour


def creer_variables(conso_jour):
    """Ajoute jour de la semaine, conso d'hier et d'il y a 7 jours."""
    conso_jour = conso_jour.copy()
    conso_jour["jour_semaine"] = conso_jour["date"].dt.dayofweek
    conso_jour["conso_hier"] = conso_jour["conso_moyenne"].shift(1)
    conso_jour["conso_7j"] = conso_jour["conso_moyenne"].shift(7)
    return conso_jour.dropna().reset_index(drop=True)


def preparer(chemin):
    """Enchaîne les trois étapes et renvoie le tableau prêt pour le modèle."""
    df = charger_donnees(chemin)
    conso_jour = regrouper_par_jour(df)
    return creer_variables(conso_jour)
import pandas as pd
from bokeh.plotting import figure,show

# Importations des bases de données ---
df_croisieres = pd.read_csv("trafic-croisieres-region-bretagne.csv",sep=";")
df_croisieres = df_croisieres.rename(columns = {"Code du port":"Code_port","Nom du port":"Port","Nombre de passagers":"Nb_passagers"})
# print(df_croisieres.head())
# print(df_croisieres.describe())

# Modifications des bases de données ---
# On ne retient que l'année de la colonne Date pour pouvoir ensuite grouper par année
# df_croisieres['Date'].to_period('A')
# df_croisieres = df_croisieres.groupby("Port","Date")
# print(df_croisieres.head())


# Graphiques ---
g_crois = figure(title = "Répartition du nombre de passagers dans les croisières en Bretagne")
# g_crois.vbar(df_croisieres["Nb_passagers"],fill_alpha = df_croisieres["Port"],width = 0.5)
# show(g_crois)


import pandas as pd
from bokeh.plotting import figure,show
from bokeh.models import ColumnDataSource


################# Importations des bases de données ---
pd.set_option("display.max_columns",19) # pour afficher tout 

df_croisieres = pd.read_csv("trafic-croisieres-region-bretagne.csv",sep=";")
df_croisieres = df_croisieres.rename(columns = {"Code du port":"Code_port","Nom du port":"Port","Nombre de passagers":"Nb_passagers"})
# print(df_croisieres.head())
# print(df_croisieres.describe())

df_ferries = pd.read_csv('trafic-ferries-region-bretagne.csv', sep=';')
print(df_ferries.head())
print(df_ferries.describe())


################ Modifications des bases de données ---

###### Modification croisiere
# On ne retient que l'année de la colonne Date pour pouvoir ensuite grouper par année
# df_croisieres['Date'].to_period('A')
# df_croisieres = df_croisieres.groupby("Port","Date")
# print(df_croisieres.head())

###### Modification feries

# Filtrer les données pour ne garder que les ports de Roscoff et Saint-Malo
df_ferries = df_ferries[df_ferries['Nom du port'].isin(['ROSCOFF', 'SAINT-MALO'])]

# Créer une source de données pour Roscoff
source_roscoff = ColumnDataSource(df_ferries[df_ferries['Nom du port'] == 'ROSCOFF'].groupby(['Date'])['Nombre de passagers'].sum().reset_index())

# Créer une source de données pour Saint-Malo
source_saintmalo = ColumnDataSource(df_ferries[df_ferries['Nom du port'] == 'SAINT-MALO'].groupby(['Date'])['Nombre de passagers'].sum().reset_index())



print(source_roscoff)
###################### Graphiques ---

#####  Graphique Marie 
#g_crois = figure(title = "Répartition du nombre de passagers dans les croisières en Bretagne")
# g_crois.vbar(df_croisieres["Nb_passagers"],fill_alpha = df_croisieres["Port"],width = 0.5)
# show(g_crois)


#### Graphique Oriane 
# Créer un graphique 
# Créer un graphique en utilisant Bokeh
p = figure(title='Somme des passagers pour les ports de Roscoff et Saint-Malo', x_axis_label='Date', y_axis_label='Nombre de passagers')

# Tracer les courbes
p.line(x='Date', y='Nombre de passagers', source=source_roscoff, line_width=2, color='blue', legend_label='Roscoff')
#p.line(x='Date', y='Nombre de passagers', source=source_saint_malo, line_width=2, color='red', legend_label='Saint-Malo')

# Afficher la légende
p.legend.location = "top_left"

# Afficher le graphique
show(p)




import pandas as pd
from bokeh.plotting import figure,show
from bokeh.models import ColumnDataSource, ColorPicker, CustomJS, NumeralTickFormatter,CategoricalColorMapper
from bokeh.layouts import row, column
from bokeh.palettes import Spectral

################# Importations des bases de données ---
pd.set_option("display.max_columns",19) # pour afficher tout 

df_croisieres = pd.read_csv("trafic-croisieres-region-bretagne.csv",sep=";")
df_croisieres = df_croisieres.rename(columns = {"Code du port":"Code_port","Nom du port":"Port","Nombre de passagers":"Nb_passagers"})
# print(df_croisieres.head())
# print(df_croisieres.describe())

df_ferries = pd.read_csv('trafic-ferries-region-bretagne.csv', sep=';', parse_dates=['Date'])
# print(df_ferries.head())
# print(df_ferries.describe())


################ Modifications des bases de données ---

###### Modification croisiere
# On créé la colonne Annee afin de pouvoir grouper les données
df_croisieres["Date"] = pd.to_datetime(df_croisieres["Date"]).dt.year
# print(df_croisieres.head())
# On groupe par port et par année et on somme le nombre de passagers pour réaliser le graphique
df_croisieres = df_croisieres.groupby(["Port","Date"],as_index=False)
df_croisieres = df_croisieres.agg({"Nb_passagers":sum})
print(df_croisieres)

# Créer une source de données pour le graphique
source_croisieres = ColumnDataSource(df_croisieres)

###### Modification feries
# Tri de la date
df = df_ferries.sort_values('Date')
# Créer des sources de données pour Roscoff et Saint-Malo
source_roscoff = ColumnDataSource(df[df['Nom du port'] == 'ROSCOFF'])
source_saint_malo = ColumnDataSource(df[df['Nom du port'] == 'SAINT-MALO'])

# Créer une source de données pour le graphique
source = ColumnDataSource(df)

##################### Widgets ---
# Créer des widgets colorPickers pour chaque courbe
colorpicker_roscoff = ColorPicker(title='Couleur de la courbe Roscoff', color='blue')
colorpicker_saint_malo = ColorPicker(title='Couleur de la courbe Saint-Malo', color='red')




###################### Graphiques ---

#####  Graphique Marie 
ports = df_croisieres["Port"].unique()
palette_couleurs = CategoricalColorMapper(factors=ports, palette=Spectral[3])
g_crois = figure(title = "Répartition du nombre de passagers dans les croisières en Bretagne",
                 y_axis_label='Nombre de passagers')
g_crois.vbar(x = "Date",top = "Nb_passagers",fill_color = {'field': 'Port', 'transform': palette_couleurs},source = source_croisieres,
             width = 0.5, legend_field = "Port")
show(g_crois)


#### Graphique Oriane 
# Créer une figure
p = figure(title='Trafic des ferries en Bretagne', x_axis_type='datetime')

# Ajouter les courbes
p_roscoff = p.line(x='Date', y='Nombre de passagers', source=source_roscoff, legend_label='Roscoff', color=colorpicker_roscoff.color, line_width=2, line_alpha=0.8)
p_saint_malo = p.line(x='Date', y='Nombre de passagers', source=source_saint_malo, legend_label='Saint-Malo', color=colorpicker_saint_malo.color, line_width=2, line_alpha=0.8)

# Configuration de l'axe des ordonnées
p.yaxis.formatter = NumeralTickFormatter(format='0,0')

# Créer une fonction de callback pour mettre à jour la couleur de la courbe Roscoff
callback_roscoff = CustomJS(args=dict(p=p_roscoff, colorpicker=colorpicker_roscoff), code="""
    p.glyph.line_color = colorpicker.color;
""")

# Créer une fonction de callback pour mettre à jour la couleur de la courbe Saint-Malo
callback_saint_malo = CustomJS(args=dict(p=p_saint_malo, colorpicker=colorpicker_saint_malo), code="""
    p.glyph.line_color = colorpicker.color;
""")

# Ajouter les callbacks aux widgets colorPickers
colorpicker_roscoff.js_on_change('color', callback_roscoff)
colorpicker_saint_malo.js_on_change('color', callback_saint_malo)

# Modifier l'apparence du graphique
p.legend.location = 'top_left'
p.legend.click_policy = 'mute'

# Afficher le graphique et les widgets colorPickers
show(row(p, column(colorpicker_roscoff, colorpicker_saint_malo)))



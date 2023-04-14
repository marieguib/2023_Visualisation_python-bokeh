import pandas as pd
from pandas import DataFrame
import numpy as np
import json
from bokeh.plotting import figure,show
from bokeh.models import ColumnDataSource, Spinner, ColorPicker, CustomJS, NumeralTickFormatter,CategoricalColorMapper,HoverTool
from bokeh.models import TabPanel, Tabs, Div,DataTable,TableColumn, Paragraph
from bokeh.layouts import row, column,Column
from bokeh.palettes import Category20b,Category20
from bokeh.transform import factor_cmap
from bokeh.themes import Theme
from bokeh.io import curdoc
from PIL import Image

################# Fonctions ---

def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)

def analyse_cites(data):
    #Construction d'un dataframe : une colonne commune, une colonne code insee, une colonne coordonnéees
    commune = []
    code_insee = []
    coordsx = []  # Pour chaque zone, liste des coordonnées x de la polyligne
    coordsy = []  # Pour chaque zone, liste des coordonnées y de la polyligne

    for cite in data :
        commune.append(cite["nom"])
        code_insee.append(cite["code_insee"])
        coords = cite["geo_point_2d"]
        x,y = coor_wgs84_to_web_mercator(coords["lon"],coords["lat"])
        coordsx.append(x)
        coordsy.append(y)
    
    df = DataFrame({'Commune': commune, 'Code Insee': code_insee, 'x':coordsx,'y':coordsy})
    return df   

def analyse_fete(data):
    #Construction d'un dataframe : une colonne denomination, une colonne tarif, une colonne coordonnéees
    lieu = []
    tarif = []
    type = []
    coordsx = []  # Pour chaque zone, liste des coordonnées x de la polyligne
    coordsy = []  # Pour chaque zone, liste des coordonnées y de la polyligne


    for manif in data:
        lieu.append(manif["detailidentadressecommune"])
        tarif.append(manif["tarifentree"])
        type.append(manif['syndicobjectname'])
        x, y = coor_wgs84_to_web_mercator(manif["point_geo"]['lon'],manif["point_geo"]['lat'])
        coordsx.append(x)
        coordsy.append(y)
    

    df = DataFrame({ 'lieu': lieu, 'tarif': tarif,'type': type,'x': coordsx, 'y': coordsy})
    return df
#################  Création du thème du projet ---

theme_projet = Theme(
    json={
        'attrs': {
            'figure': {
                'background_fill_color': 'darkgrey',
                'background_fill_alpha':0.6,
                'border_fill_color': 'white',
                'outline_line_color': 'white',
            },
            'Grid': {
                'grid_line_color': 'white',
                'grid_line_alpha': 0.2,
            },
            'Axis': {
                'axis_line_color': 'white',
                'major_tick_line_color': 'red',
                'minor_tick_line_color': '#D9E1E6',
                'axis_label_text_color': 'darkgrey',
                'axis_label_text_font': 'Verdana',
                'axis_label_text_font_size': '12pt',
                'major_label_text_color': 'darkgrey',
                'major_label_text_font': 'Verdana'
            },
            'Legend': {
                'background_fill_color': '#F0F2F6',
                'border_line_color': '#FFFFFF',
                'label_text_color': '#555555',
                'label_text_font': 'Verdana',
                'label_text_font_size': '10pt',
            },
            'Title': {
                'text_color': '#555555',
                'text_font': 'Verdana',
                'text_font_size': '14pt',
            }
        }
    }
)

curdoc().theme = theme_projet

#################  Présentation de notre projet ---

titre = Div(text = """<h1> Présentation de notre projet </h1>""")

pres = Div(text ="""
<p> Ce cours a pour but de montrer comment intégrer du code html</p>
<p> Lors de notre étude, nous avons choisi d'étudier le tourisme et les activités en Bretagne. </p>
<p> Nous avons décider de nous focaliser sur 3 thèmes importants :
<ul>
    <li> L'activité des différents ports concernant les départs en ferries et en croisières </li>
    <li> Les petites cités de caractères </li>
    <li> Les fêtes et manifestations </li>
</ul>
<p> Ces sujets nous ont semblé pertinents à étudier car ils concentrent les activités intéressantes et ludiques en Bretagne. </p>""")

lien = Div(text= """<p> <a href="http://www.univ-rennes2.fr ">Un lien vers le site de l'Université</a>  </p>""")


auteures = Div(text = """
        <h2> Auteures du projet </h2>
        <ul>
            <li> Marie Guibert </li> 
            <li> Oriane Duclos </li>
        </ul>""")

img = Div(text="""<img src="saint-malo.jpg" width="600"/>""")

layout_pres = column(titre,lien, row(pres,img))

################# Importations des bases de données ---
pd.set_option("display.max_columns",19) # pour afficher tout 

### Importation base de donnée croissière
df_croisieres = pd.read_csv("trafic-croisieres-region-bretagne.csv",sep=";")
df_croisieres = df_croisieres.rename(columns = {"Code du port":"Code_port","Nom du port":"Port","Nombre de passagers":"Nb_passagers"})
# print(df_croisieres.head())
# print(df_croisieres.describe())


### Importation base de donnée ferries
df_ferries = pd.read_csv('trafic-ferries-region-bretagne.csv', sep=';', parse_dates=['Date'])
# print(df_ferries.head())
# print(df_ferries.describe())


### Importation base de donnée petites cités de caractère
with open("petites-cites-de-caractere-en-bretagne.json","r",encoding='utf-8') as jsonfile :
    data_cites = json.load(jsonfile)

df_cites = analyse_cites(data_cites)
# print(df_cites)
# print(df_cites.head())
# print(df_cites.describe())

### Importation base de donnée fetes et manifestations

with open('bretagne-fetes-et-manifestations.json') as mon_fichier:
    data_fete = json.load(mon_fichier)    

df_fete = analyse_fete(data_fete)
# print(df_fete)

# print(df_fete.describe())
# print(df_fete.head())

################ Modifications des bases de données ---

###### Modification croisiere
# On créé la colonne Annee afin de pouvoir grouper les données
df_croisieres["Date"] = pd.to_datetime(df_croisieres["Date"]).dt.year
# print(df_croisieres.head())
# On groupe par port et par année et on somme le nombre de passagers pour réaliser le graphique
df_croisieres = df_croisieres.groupby(["Port","Date"],as_index=False)
df_croisieres = df_croisieres.agg({"Nb_passagers":sum})
# print(df_croisieres)

# Créer une source de données pour le graphique
source_croisieres = ColumnDataSource(df_croisieres)



###### Modification ferries
# Tri de la date
df = df_ferries.sort_values('Date')
# Créer des sources de données pour Roscoff et Saint-Malo
source_roscoff = ColumnDataSource(df[df['Nom du port'] == 'ROSCOFF'])
source_saint_malo = ColumnDataSource(df[df['Nom du port'] == 'SAINT-MALO'])

# Créer une source de données pour le graphique
source = ColumnDataSource(df)


###### Modification cites
source_cites = ColumnDataSource(df_cites)
# print(source_cites.column_names)

###### Modification fetes 
#print(df_fete.columns)
#print(df_fete['tarif'].unique())
type_tarif = ['Tarifs non communiqués', 'Payant', 'Gratuit', 'Libre participation']

source_fete = ColumnDataSource(df_fete)


##################### Widgets ---
# Graphique croisieres
# Créer des widgets colorPickers pour chaque courbe
colorpicker_roscoff = ColorPicker(title='Couleur de la courbe Roscoff', color='#393b79')
colorpicker_saint_malo = ColorPicker(title='Couleur de la courbe Saint-Malo', color='#6b6ecf')

# Carte des cites de caractère
hover_tool = HoverTool(tooltips=[('Commune', '@Commune')])
# trouver une image à ajouter quand on survole 
# lien de la ville à ajouter quand on survole


###################### Graphiques ---

#####  Graphique croissiere
ports = df_croisieres["Port"].unique()
palette_couleurs = CategoricalColorMapper(factors=ports, palette=Category20b[3])
g_crois = figure(title = "Répartition du nombre de passagers \ndans les croisières en Bretagne",
                 y_axis_label='Nombre de passagers')
g_crois.vbar(x = "Date",top = "Nb_passagers",fill_color = {'field': 'Port', 'transform': palette_couleurs}, line_color = None, source = source_croisieres,
             width = 0.5, legend_field = "Port")
# show(g_crois)

outilsurvol3 = HoverTool(tooltips=[( "Nb de passager",'@Nb_passagers')])
g_crois.add_tools(outilsurvol3)


#### Graphique feries
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
p.legend.title = ' 2 Ports'
p.legend.label_text_font = "arial"
p.legend.label_text_font_style = "italic"
p.legend.label_text_color = "white"
p.legend.border_line_width = 2
p.legend.border_line_color = "red" 
p.legend.border_line_alpha = 0.8
p.legend.background_fill_color = "red"
p.legend.background_fill_alpha = 0.2

# Créer l'outil HoverTool
hover_ferries = HoverTool(
    tooltips=[
        ('Date', '@Date{%Y-%m}'),
        ('Nombre de passagers', '@{Nombre de passagers}{0,0}'),
    ],
    formatters={
        'Date': 'datetime', # Formater la date au format 'YYYY-MM-DD'
        'Nombre de passagers': 'printf', # Formater le nombre de passagers avec des virgules
    },
    mode='vline', # Afficher une ligne verticale sur le point survolé
)

# Ajouter l'outil HoverTool à la figure
p.add_tools(hover_ferries)

# Afficher le graphique et les widgets colorPickers
# show(row(p, column(colorpicker_roscoff, colorpicker_saint_malo)))

## Table croisières 
columns = [
          TableColumn(field="Port", title="Nom du port"),
        TableColumn(field="Date", title="Date"),
        TableColumn(field="Nb_passagers", title="Nombre de passagers")  
    ]
data_table_croisieres = DataTable(source=source_croisieres, columns=columns, width=400, height=280)


#### Carte petites cités de caractères 
carte_cites = figure(x_axis_type="mercator", y_axis_type="mercator", title="Petites cités de caractère en Bretagne")
carte_cites.add_tile("CartoDB Positron")
points = carte_cites.circle("x","y",source=source_cites,line_color = None,fill_color='#9c9ede',size=30)
carte_cites.add_tools(hover_tool)

picker_cites = ColorPicker(title="Couleur de ligne",color=points.glyph.fill_color) 
spinner_cites = Spinner(title="Taille des cercles", low=0,high=60, step=5, value=points.glyph.size)
picker_cites.js_link('color', points.glyph, 'fill_color')
spinner_cites.js_link("value", points.glyph, "size") 

layout_cites = row(carte_cites, column(picker_cites,spinner_cites))
# show(layout)

### Carte fete et manif 

carte_fete = figure(x_axis_type="mercator", y_axis_type="mercator", title="Lieux de manifestations et de fêtes")
carte_fete.add_tile("CartoDB Positron")
carte_fete.circle("x","y",source=source_fete,color=factor_cmap('tarif', palette=['#393b79','#6b6ecf','#9c9ede'], factors=type_tarif),size=8, alpha = 0.5)

# Ajout des informations de survol pour les icônes de fête
hover_fete = HoverTool(
    tooltips=[('Lieu', '@lieu'), ('Tarif', '@tarif'), ('Type', '@type')],
    mode='mouse'
)
carte_fete.add_tools(hover_fete)


# Affichage de la carte
#show(carte_fete)

########## Texte 

div2 = Div(text=""" <h1> Graphique n°2 </h1> <p> Ce graphique vous montre le trafic des ferries en Bretagne de 2017 à 2022. On y voit en phénomène de saisonnalité. On suppose qu'il y a beaucoup de trafic l'été et moins l'hiver. On peut voir un trafic reste inexistant durant la periode du Covid-19 en 2020-2021 </p>""",styles={'text-align':'justify','color':'black','background-color':'lavender','padding':'15px','border-radius':'10px'})
par2 = Div(text="Ces widgets permettent de choisir la couleur des 2 ports.",styles={'text-align':'justify','color':'black','background-color':'papayawhip','padding':'15px','border-radius':'10px'})

par1 = Div(text="Ces widgets permettent de choisir la couleur des pop-up qui matérialisent la repartition du nombre de passegrs sur les différents ports",styles={'text-align':'justify','color':'black','background-color':'papayawhip','padding':'15px','border-radius':'10px'})
div1 = Div(text=""" <h1> Graphique n°1 </h1> <p> Ce diagramme en barre nous montre la répartition du nombre de passgers dans les croisières en Bretagne, ici vous voyez les 3 principaux ports de bretagne Brest, Lorient, Saint Malo. De plus, à votre droite vous pouvez "naviguez" dans la base de donnée &#160;</p>""",styles={'text-align':'justify','color':'black','background-color':'lavender','padding':'15px','border-radius':'10px'})

div3 = Div(text=""" <h1> Carte n°1 </h1> <p> Cette carte représente les petites cités de caractère en Bretagne. A vous de trouvez votre futur destination de vacances ! &#160;</p>""",styles={'text-align':'justify','color':'black','background-color':'lavender','padding':'15px','border-radius':'10px'}) 

div4 = Div(text=""" <h1> Carte n°2 </h1> <p> Cette carte représente les lieux de manifestions et de fêtes de la bretagne. Les différentes couleurs représentent le type de tarif de l'évenement (payant, gratuit, libre et non communiqué</p>""",styles={'text-align':'justify','color':'black','background-color':'lavender','padding':'15px','border-radius':'10px'})


#################  Création des onglets ---

tab1 = TabPanel(child = layout_pres,title = "Présentation")
tab2 = TabPanel(child= column(div1,row(g_crois,column(par1,data_table_croisieres))), title="Croisières")
tab3 = TabPanel(child=column(div2,row(p,column(par2,colorpicker_roscoff, colorpicker_saint_malo))), title="Ferries")
tab4 = TabPanel(child = column(div3, row(layout_cites)), title = "Cités de caractère")
tab5 = TabPanel(child = column(div4, row(carte_fete)), title = "Fêtes et manifestations")

tabs = Tabs(tabs= [tab1,tab2,tab3,tab4,tab5])
show(tabs)
import pandas as pd
from pandas import DataFrame
import numpy as np
import json
from datetime import datetime
from bokeh.plotting import figure,show
from bokeh.models import ColumnDataSource, Spinner, ColorPicker, CustomJS, NumeralTickFormatter,CategoricalColorMapper,HoverTool
from bokeh.models import TabPanel, Tabs, Div,DataTable,TableColumn, Paragraph, Slider, Dropdown
from bokeh.layouts import row, column,Column
from bokeh.palettes import Category20b,Category20
from bokeh.transform import factor_cmap
from bokeh.themes import Theme
from bokeh.io import curdoc
from PIL import Image

#######################################################################################################################
############################################## Créations de fonctions #################################################
#######################################################################################################################

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
#######################################################################################################################
######################################### Création du thème du projet #################################################
#######################################################################################################################

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
                'location' : 'top_left',
                'click_policy' : 'mute',
                'border_line_width' : 2,
                'label_text_font_style' : "italic"
            },
            'Title': {
                'text_color': '#555555',
                'text_font': 'Verdana',
                'text_font_size': '14pt'
            }
        }
    }
)

curdoc().theme = theme_projet

#######################################################################################################################
############################################## Présentation du projet #################################################
#######################################################################################################################

titre = Div(text = """<h1> Présentation de notre projet </h1>""",styles = {"color":"darkblue"})

nous = Div(text = """<h2> Duclos Oriane & Guibert Marie </h2>""",styles = {"color":"lightblue"})

pres = Div(text ="""
<p> Lors de notre étude, nous avons choisi d'étudier le tourisme et les activités en Bretagne. </p>
<p> Nous avons décider de nous focaliser sur 3 thèmes importants :
<ul>
    <li> L'activité des différents ports concernant les départs en ferries et en croisières </li>
    <li> Les petites cités de caractères </li>
    <li> Les fêtes et manifestations </li>
</ul>
<p> Ces sujets nous ont semblé pertinents à étudier car ils concentrent les activités intéressantes et ludiques en Bretagne. </p>""")

lien = Div(text= """<p> <a href=https://data.bretagne.bzh/ ">Un lien vers le site de nos bases de données</a>  </p>""")
lien_git = Div(text= """<p> <a href=https://github.com/marieguib/Projet_visualisation_python/">Un lien vers le github du projet</a>  </p>""")


auteures = Div(text = """
        <h2> Auteures du projet </h2>
        <ul>
            <li> Marie Guibert </li> 
            <li> Oriane Duclos </li>
        </ul>""")

img = Div(text="""<img src="saint-malo.jpg" width="600"/>""")

titre2 = Div(text = """<h1> Le tourisme en Bretagne </h1>""",styles = {"color":"darkblue"})

layout_pres = row(column(titre,nous,lien,lien_git, pres,titre2),img)

#######################################################################################################################
######################################### Importations des bases de données ###########################################
#######################################################################################################################

pd.set_option("display.max_columns",19) # Option pour afficher toutes les colonnes

### Importation base de données croisières ---
df_croisieres = pd.read_csv("trafic-croisieres-region-bretagne.csv",sep=";")
# On renomme les colonnes pour avoir  un data-frame plus clair
df_croisieres = df_croisieres.rename(columns = {"Code du port":"Code_port","Nom du port":"Port","Nombre de passagers":"Nb_passagers"})
# print(df_croisieres.head())
# print(df_croisieres.describe())


### Importation base de données ferries ---
df_ferries = pd.read_csv('trafic-ferries-region-bretagne.csv', sep=';', parse_dates=['Date'])
# print(df_ferries.head())
# print(df_ferries.describe())


### Importation base de données petites cités de caractère ---
with open("petites-cites-de-caractere-en-bretagne.json","r",encoding='utf-8') as jsonfile :
    data_cites = json.load(jsonfile)
df_cites = analyse_cites(data_cites)
# print(df_cites)
# print(df_cites.head())
# print(df_cites.describe())

### Importation base de données fetes et manifestations ---
with open('bretagne-fetes-et-manifestations.json') as mon_fichier:
    data_fete = json.load(mon_fichier)    
df_fete = analyse_fete(data_fete)
# print(df_fete)
# print(df_fete.describe())
# print(df_fete.head())

#######################################################################################################################
######################################### Modifications des bases de données ##########################################
#######################################################################################################################

### Modification croisieres ---
# On créé une modifie la colonne "Date" dans le data-frame afin de pouvoir grouper les données par année
df_croisieres["Date"] = pd.to_datetime(df_croisieres["Date"]).dt.year # on recupère seulement l'année de la colonne Date initiale 
# print(df_croisieres.head())
# On groupe par port et par année
# On somme ensuite le nombre de passagers pour réaliser le graphique
df_croisieres = df_croisieres.groupby(["Port","Date"],as_index=False) # regroupement
df_croisieres = df_croisieres.agg({"Nb_passagers":sum}) # somme
# print(df_croisieres) # vérification du data-frame

# Créer une source de données pour le graphique
source_croisieres = ColumnDataSource(df_croisieres)


### Modification ferries ---
# On tri le data-frame par la date
df = df_ferries.sort_values('Date')

# Créer des sources de données pour le graphique concernant les deux ports : Roscoff et Saint-Malo
source_roscoff = ColumnDataSource(df[df['Nom du port'] == 'ROSCOFF'])
source_saint_malo = ColumnDataSource(df[df['Nom du port'] == 'SAINT-MALO'])

# Créer une source de données pour le graphique
source = ColumnDataSource(df)


### Modification cites ---
# Créer une source de données pour le graphique
source_cites = ColumnDataSource(df_cites)
# print(source_cites.column_names)

### Modification fetes ---
# On récupère les noms de colonnes
# print(df_fete.columns)
# On observe les différentes modalités de la colonne 'tarif'
#print(df_fete['tarif'].unique())
# On créé ensuite la liste des modalités :
type_tarif = ['Tarifs non communiqués', 'Payant', 'Gratuit', 'Libre participation']

# Créer une source de données pour le graphique
source_fete = ColumnDataSource(df_fete)

df_tarifs = pd.read_csv("bretagne-fetes-et-manifestations.csv",sep=";")
df_tarifs = df_tarifs.rename(columns = {"SyndicObjectID":"ID",
                                        "Published":"Date",
                                        "SyndicObjectName":"Nom",
                                        "GmapLatitude" : "Latitude",
                                        "GmapLongitude" : "Longitude",
                                        "DetailIDENTADRESSECP" :"CP",
                                        "DetailIDENTADRESSECOMMUNE" : "Commune",
                                        "TARIFENTREE" : "Tarifs"})

Compte = df_tarifs.groupby(["Tarifs"]).size()

# Création du datasource
source_tarifs = ColumnDataSource(data = dict(x = type_tarif, counts = Compte, color = Category20b[4]))


#######################################################################################################################
############################################## Créations de widgets ###################################################
#######################################################################################################################

### Graphique croisieres ---
# Créer des widgets colorPickers pour chaque courbe
# L'utilisateur pourra ensuite choisir la couleur qu'il souhaite grâce à un sélecteur
colorpicker_roscoff = ColorPicker(title='Couleur de la courbe Roscoff', color='#393b79') # on initialise une couleur de départ pour rester dans le thème
colorpicker_saint_malo = ColorPicker(title='Couleur de la courbe Saint-Malo', color='#6b6ecf')
# Création d'un outil de survol pour afficher le nombre de passagers pour chaque port et selon l'année
outilsurvol3 = HoverTool(tooltips=[( "Nb de passager",'@Nb_passagers')])

### Graphique ferries ---
# Création d'un outil de survol qui affiche la date et le nombre de passagers
hover_ferries = HoverTool(
    tooltips=[
        ('Nombre de passagers', '@{Nombre de passagers}{0,0}'),
    ],
    formatters={
        'Nombre de passagers': 'printf', # Formater le nombre de passagers avec des virgules
    },
    mode='vline', # Afficher une ligne verticale sur le point survolé
)

### Carte des cites de caractères ---
# Création d'un outil de survol qui affiche la commune lorsque l'on passe la souris dessus 
hover_tool = HoverTool(tooltips=[('Commune', '@Commune')])


### Carte des fêtes et manifestations ---
hover_fete = HoverTool(
    tooltips=[('Lieu', '@lieu'), ('Tarif', '@tarif'), ('Type', '@type')],
    mode='mouse'
)

### Type de tarif graphique ---
hover_tarifs = HoverTool(
    tooltips=[('Compte', '@counts')],
    mode='mouse'
)



#######################################################################################################################
################################################### Graphiques ########################################################
#######################################################################################################################

###  Graphique croisieres ---
# On créé une variable contenant le nom de chaque port de la base de données
ports = df_croisieres["Port"].unique()
# print(ports) 

# Création d'une palette de couleurs pour le graphique
palette_couleurs = CategoricalColorMapper(factors=ports, palette=Category20b[3]) # il y a 3 ports donc on sélectionne 3 couleurs

# Création de la figure
g_crois = figure(title = "Répartition du nombre de passagers \ndans les croisières en Bretagne",
                 y_axis_label='Nombre de passagers')
# Création du graphique 
g_crois.vbar(x = "Date",top = "Nb_passagers",fill_color = {'field': 'Port', 'transform': palette_couleurs}, line_color = None, source = source_croisieres,
             width = 0.5, legend_field = "Port")

# Ajout de widgets 
g_crois.add_tools(outilsurvol3)

# show(g_crois)

### Table croisières ---
columns = [
          TableColumn(field="Port", title="Nom du port"),
        TableColumn(field="Date", title="Date"),
        TableColumn(field="Nb_passagers", title="Nombre de passagers")  
    ]
data_table_croisieres = DataTable(source=source_croisieres, columns=columns, width=400, height=280)



### Graphique ferries ---
# Créer la figure
p = figure(title='Trafic des ferries en Bretagne', x_axis_type='datetime')

# Ajouter les courbes concernant le nombre de passagers dans chaque port
p_roscoff = p.line(x='Date', y='Nombre de passagers', source=source_roscoff, legend_label='Roscoff', color=colorpicker_roscoff.color, line_width=2, line_alpha=0.8)
p_saint_malo = p.line(x='Date', y='Nombre de passagers', source=source_saint_malo, legend_label='Saint-Malo', color=colorpicker_saint_malo.color, line_width=2, line_alpha=0.8)

# Ajout d'un titre à la légende
p.legend.title = ' 2 Ports'

# Configuration de l'axe des ordonnées
p.yaxis.formatter = NumeralTickFormatter(format='0,0')

# Ajout d'un arrière plan dans le graphique
url = "https://static.vecteezy.com/ti/vecteur-libre/t2/15181418-icone-de-navire-avant-style-de-contour-vectoriel.jpg"
arriere_plan = Div(text = '<div style="position: absolute; left:100px; top:20px"><img src=' + url + ' style="width:560px; height:560px; opacity: 0.2"></div>')

# Créer une fonction de callback pour mettre à jour la couleur de la courbe Roscoff lorsque l'utilisateur sélectionne une couleur spécifique de courbe voulue
callback_roscoff = CustomJS(args=dict(p=p_roscoff, colorpicker=colorpicker_roscoff), code="""
    p.glyph.line_color = colorpicker.color;
""")

# Créer une fonction de callback pour mettre à jour la couleur de la courbe Saint-Malo lorsque l'utilisateur sélectionne une couleur spécifique de courbe voulue
callback_saint_malo = CustomJS(args=dict(p=p_saint_malo, colorpicker=colorpicker_saint_malo), code="""
    p.glyph.line_color = colorpicker.color;
""")

# Ajouter les callbacks aux widgets colorPickers
colorpicker_roscoff.js_on_change('color', callback_roscoff)
colorpicker_saint_malo.js_on_change('color', callback_saint_malo)

# Ajouter l'outil HoverTool à la figure
p.add_tools(hover_ferries)

# Afficher le graphique et les widgets colorPickers
layout_ferries = row(p, column(colorpicker_roscoff, colorpicker_saint_malo))
# show(row(p, column(colorpicker_roscoff, colorpicker_saint_malo)))


### Carte petites cités de caractères  ---
# Création de la figure 
carte_cites = figure(x_axis_type="mercator", y_axis_type="mercator", title="Petites cités de caractère en Bretagne")
carte_cites.add_tile("OSM")

# Ajout de cercles pour chaque cité de caractère
points = carte_cites.circle("x","y",source=source_cites,line_color = None,fill_color='#9c9ede',size=30) # on initialise la taille des cercles à 30 

# Création de widgets
picker_cites = ColorPicker(title="Couleur de ligne",color=points.glyph.fill_color)  #règle la couleur des cercles
# spinner_cites = Spinner(title="Taille des cercles", low=0,high=60, step=5, value=points.glyph.size) #règle la taille des cercles
slider_cites = Slider(start = 5, end = 100, value = 30, step = 5, title= "Taille des cercles")
# Créer une fonction de callback pour mettre à jour la couleur et la taille
picker_cites.js_link('color', points.glyph, 'fill_color')
# spinner_cites.js_link("value", points.glyph, "size") 
slider_cites.js_link("value", points.glyph, "size") 

# Ajout des widgets
carte_cites.add_tools(hover_tool)

# Affichage 
# layout_cites = row(carte_cites, column(picker_cites,spinner_cites))
# show(layout_cites)

### Carte fetes et manifs ---
# Création de la figure
carte_fete = figure(x_axis_type="mercator", y_axis_type="mercator", title="Lieux de manifestations et de fêtes")
carte_fete.add_tile("CartoDB Positron")
# Ajout de cercles pour chaque lieu de fête / manifestation
carte_fete.circle("x","y",source=source_fete,color=factor_cmap('tarif', palette=['#393b79','#6b6ecf','#9c9ede'], factors=type_tarif),size=8, alpha = 0.5)

# Ajout du widget
# Informations de survol pour les icônes de fête 
carte_fete.add_tools(hover_fete)



# Affichage de la carte
# show(carte_fete)

### Graphique tarification  ---
t = figure(title = "Nombre d'évènements rangés par tarifs",
            x_range = type_tarif,
            x_axis_label = "Tarifs",
            y_axis_label= "Nombre d'évènements")

t.vbar( x = 'x',  top = 'counts', source = source_tarifs, color = 'color')

# Ajout des widgets
t.add_tools(hover_tarifs)


#######################################################################################################################
######################################## Commentaires graphiques ######################################################
#######################################################################################################################

### Commentaire graphique ferries ---
div2 = Div(text=""" <h1> Graphique n°2 </h1> 
        <p> Ce graphique vous montre le trafic des ferries en Bretagne de 2017 à 2022. \n
        On y voit en phénomène de saisonnalité. On suppose qu'il y a beaucoup de trafic l'été et moins l'hiver. On remarque aussi un trafic inexistant durant la periode du Covid-19 en 2020-2021 </p>""",styles={'text-align':'justify','color':'black','background-color':'lavender','padding':'15px','border-radius':'10px'})
par2 = Div(text="Ces widgets permettent de choisir la couleur des 2 ports :",styles={'text-align':'justify','color':'black','background-color':'papayawhip','padding':'15px','border-radius':'10px'})

### Commentaire graphique croisières ---
div1 = Div(text=""" <h1> Graphique n°1 </h1> 
        <p> Ce diagramme en barre nous montre la répartition du nombre de passagers dans les croisières en Bretagne. \n 
        Ici vous voyez les 3 principaux ports de Bretagne :
         <ul>
          <li> Brest </li>
          <li> Lorient </li>
          <li> Saint Malo </li>
         </ul>
        De plus, à votre droite vous pouvez "naviguer" dans la base de données &#160;</p>""",styles={'text-align':'justify','color':'black','background-color':'lavender','padding':'15px','border-radius':'10px'})

### Commentaire carte petites cités de caractères ---
par3 = Div(text="Ces widgets permettent de choisir la couleur des pop-ups qui matérialisent la couleur et la taille des cercles concernant les petites cités de caractère en Bretagne",styles={'text-align':'justify','color':'black','background-color':'papayawhip','padding':'15px','border-radius':'10px'})
div3 = Div(text=""" <h1> Carte n°1 </h1> 
        <p> Cette carte représente les petites cités de caractère en Bretagne. \n
        A vous de trouver votre future destination de vacances ! &#160;</p>""",styles={'text-align':'justify','color':'black','background-color':'lavender','padding':'15px','border-radius':'10px'}) 

### Commentaire carte lieux de fêtes et manifestations ---
div4 = Div(text=""" <h1> Carte n°2 et Graphique n°3</h1> 
        <p> Cette carte représente les lieux de manifestations et de fêtes de la Bretagne. \n</p>
        <p> N'hésitez pas à regarder les tarifs associés aux évènements qui vous intéressent ! Ils correspondent aux différentes couleurs présentes sur les figures (payant, gratuit, libre et non communiqué) </p>
        <p> Vous pouvez aussi voir ci-dessous un graphique du nombre d'évènements par type de tarif. </p>""",styles={'text-align':'justify','color':'black','background-color':'lavender','padding':'15px','border-radius':'10px'})


#######################################################################################################################
########################################### Création des onglets ######################################################
#######################################################################################################################

# tab1 = TabPanel(child = layout_pres,title = "Présentation")
tab2 = TabPanel(child= column(div1,row(g_crois,column(data_table_croisieres))), title="Croisières")
tab3 = TabPanel(child=column(div2,row(p,arriere_plan,column(par2,colorpicker_roscoff, colorpicker_saint_malo))), title="Ferries")
# tab4 = TabPanel(child = column(div3, row(carte_cites, column(par3,picker_cites,spinner_cites))), title = "Cités de caractère")
tab4 = TabPanel(child = column(div3, row(carte_cites, column(par3,picker_cites,slider_cites))), title = "Cités de caractère")
tab5 = TabPanel(child = column(div4, row(carte_fete,t)), title = "Fêtes et manifestations")
tabs = Tabs(tabs= [tab2,tab3,tab4,tab5])

#######################################################################################################################
################################################ Affichage final ######################################################
#######################################################################################################################

show(column(layout_pres,tabs))

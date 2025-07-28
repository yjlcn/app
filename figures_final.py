# ===============Import standard libraries=================

import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import datetime
import streamlit as st

from fonctions_xb import plot_mix_evolution_between
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb
from plotly.colors import label_rgb


# ================== Impoirtation données========
path_to_pickles = 'data/Pickles'

os.listdir(path_to_pickles)
directory = path_to_pickles

df_data_nationales = pd.read_pickle(directory + '/df_data_nationales.pkl')
df_temperatures = pd.read_pickle(directory + '/df_temperatures.pkl')
df_data_nationales_long = pd.read_pickle(directory + '/df_data_nationales_2012-23.pkl')
df_temperatures_long = pd.read_pickle(directory + '/df_temperatures_jour_2018-23.pkl')

# =============== Arranger les dataframe pour tracer les graphs =======================
df_temperatures = df_temperatures.reset_index()
df_temperatures_long = df_temperatures_long.reset_index()
df_temperatures = df_temperatures.rename(columns={"date_validite": "Date"})
df_temperatures['Date'] = pd.to_datetime(df_temperatures['Date']).dt.date
df_temperatures_long['Date'] = pd.to_datetime(df_temperatures_long['Date']).dt.date
df_temperatures_full = pd.concat([df_temperatures, df_temperatures_long], ignore_index=True)
df_temperatures_full.set_index('Date', inplace=True)
conso_nat_long = pd.DataFrame(df_data_nationales_long['Consommation'].dropna(axis=0).resample('D').mean())
avg_temp_nat_long = pd.DataFrame(df_temperatures_full.mean(axis=1), columns=['avg_temperature'])
merged = conso_nat_long.merge(avg_temp_nat_long, how='inner', left_index=True, right_index=True)
merged_D = merged.resample('D').mean()
df_temp_conso_D = merged_D.dropna()


# ====================== Titre partie thermo sencibilité ===============================

st.header("Thermo-sensibilité de la consommation")


# =============== Tracer du graphe Variation de la consommation d’énergie en fonction de la température (2014-2017) ===============
st.markdown("<h4 style='text-align: center; color: black;'>Variation de la consommation d’énergie en fonction de la température (2013-2023)</h4>", unsafe_allow_html=True)
fig = px.scatter(df_temp_conso_D, 
                 x = "avg_temperature", 
                 y = "Consommation")
fig.update_layout(
    xaxis=dict(
        title="Température (°C)",  
    ),
    yaxis=dict(
        title="Consommation (MW)"  
    ),
    xaxis_title_font=dict(size=18),  
    yaxis_title_font=dict(size=18),  
    xaxis_tickfont=dict(size=14),    
    yaxis_tickfont=dict(size=14),    
    legend_font=dict(size=14),
    shapes=[
        dict(
            type="line",
            x0=15, x1=15,    
            y0=0, y1=1,      
            xref="x",
            yref="paper",    
            line=dict(color="red", width=2, dash="dash") 
        )
    ]   
)
fig.update_traces(marker=dict(size=3))
st.plotly_chart(fig)

# ================== Thermo sencibilité ===================
st.markdown("<h4 style='text-align: center; color: black;'>Variation de la consommation d’énergie entre 0 et 15°C</h4>", unsafe_allow_html=True)

df_T15_consomation_D = df_temp_conso_D[df_temp_conso_D["avg_temperature"] <= 15]

x = df_T15_consomation_D["avg_temperature"]
y = df_T15_consomation_D["Consommation"]


a, b = np.polyfit(x, y, 1)

fig = px.scatter(df_T15_consomation_D, x="avg_temperature", y="Consommation")

x_vals = np.linspace(x.min(), x.max(), 100)
y_vals = a * x_vals + b


# ajout equation
equation_text = f"y = {a:.2f}x + b"
fig.add_annotation(x=x.mean(), y=y.mean(), text=equation_text,
                   showarrow=False, font=dict(size=14, color="red"),
                   bgcolor="white", bordercolor="red", borderwidth=1)
                
fig.add_trace(go.Scatter(
    x=x_vals, y=y_vals, mode="lines", name="Droite de régression", 
    line=dict(color='red'),
))

fig.update_layout(
    xaxis=dict(
        title="Température (°C)",  
    ),
    yaxis=dict(
        title="Consommation (MW)"  
    ),
    xaxis_title_font=dict(size=18),  
    yaxis_title_font=dict(size=18),  
    xaxis_tickfont=dict(size=14),    
    yaxis_tickfont=dict(size=14),    
    legend_font=dict(size=14),
     )

fig.update_traces(marker=dict(size=2.5))
st.plotly_chart(fig, use_container_width=True)


# =============== Tracer du graphe (2014-2023) ===============
st.markdown("<h4 style='text-align: center; color: black;'>Relation consommation-température (entre 0 et 15°C), année 2014 vs 2023</h4>", unsafe_allow_html=True)

# faire pour 2014
df_2014 = df_temp_conso_D[(df_temp_conso_D.index.year == 2014) & (df_temp_conso_D["avg_temperature"] > 0) & (df_temp_conso_D["avg_temperature"] < 15)]
    
x_2014 = df_2014["avg_temperature"]
y_2014 = df_2014["Consommation"]
a_2014, b_2014 = np.polyfit(x_2014, y_2014, 1)
x_vals_2014 = np.linspace(x_2014.min(), x_2014.max(), 100)
y_vals_2014 = a_2014 * x_vals_2014 + b_2014

# pour 2023
df_2023 = df_temp_conso_D[(df_temp_conso_D.index.year == 2023) & (df_temp_conso_D["avg_temperature"] > 0) & (df_temp_conso_D["avg_temperature"] < 15)]

x_2023 = df_2023["avg_temperature"]
y_2023 = df_2023["Consommation"]
a_2023, b_2023 = np.polyfit(x_2023, y_2023, 1)
x_vals_2023 = np.linspace(x_2023.min(), x_2023.max(), 100)
y_vals_2023 = a_2023 * x_vals_2023 + b_2023

  
# afficher le graph avec la droite de regresison
fig = px.scatter(df_2014, x="avg_temperature", y="Consommation", color_discrete_sequence=["#CFBDBD"])

fig.data[0].name = "Points 2014"

fig.add_trace(go.Scatter(
    x=df_2014["avg_temperature"],
    y=df_2014["Consommation"],
    mode="markers",
    name="Points 2014",
    marker=dict(color="#CFBDBD")
))

# rajouter 2023
fig.add_trace(go.Scatter(x=df_2023["avg_temperature"], y=df_2023["Consommation"],
                         mode="markers", name="Points 2023",
                         marker=dict(color="#868484")))

# ajout droite de regretion :
fig.add_trace(go.Scatter(x=x_vals_2014, y=y_vals_2014, mode="lines", line=dict(color='red'), showlegend=False))
fig.add_trace(go.Scatter(x=x_vals_2023, y=y_vals_2023, mode="lines", line=dict(color='#007BB4'), showlegend=False))

# titre graphe
fig.update_layout(
    xaxis=dict(
        title="Température (°C)",  
    ),
    yaxis=dict(
        title="Consommation (MW)"  
    ),
    xaxis_title_font=dict(size=18),  
    yaxis_title_font=dict(size=18),  
    xaxis_tickfont=dict(size=14),    
    yaxis_tickfont=dict(size=14),    
    legend_font=dict(size=14)
)
# taille des points
fig.update_traces(marker=dict(size=3.5))

# Annotation pour 2014
fig.add_annotation(
    x=x_2014.mean(), y=y_2014.mean() + 10000,  
    text=f"Régression 2014 : y = <b>{a_2014:.0f}</b> x + b",
    showarrow=False,
    font=dict(size=13, color="red"),
    bgcolor="white",
    bordercolor="red",
    borderwidth=1
)

# Annotation pour 2023
fig.add_annotation(
    x=x_2023.mean(), y=y_2023.mean() - 10000,  
    text=f"Régression 2023 : y = <b>{a_2023:.0f}</b> x + b",
    showarrow=False,
    font=dict(size=13, color="#007BB4"),
    bgcolor="white",
    bordercolor="#007BB4",
    borderwidth=1
)

st.plotly_chart(fig)


# =============== Evolution thermosencibilité au cours du temps ===============


st.markdown("<h4 style='text-align: center; color: black;'>Évolution de la thermosensibilité au cours du temps</h4>", unsafe_allow_html=True)


annees = [2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
conso = {}

annee_min = df_temp_conso_D.index.year.min()
annee_max = 2017


def plot_regression_for_year(df, annee):

    # selectionner suelement l'annee passer en argumenbt et une temperature netre 0 et 15 degree
    df_year = df[(df.index.year == annee) & (df["avg_temperature"] > 0) & (df["avg_temperature"] < 15)]

    # calculer la droite de regression
    x = df_year["avg_temperature"]
    y = df_year["Consommation"]
    a, _ = np.polyfit(x, y, 1)
    return a

# pour chaque année du df
for annee in annees :
    a = plot_regression_for_year(df_temp_conso_D, annee)
    conso[annee] = -a

# afficher evolution du coef diecteur
df = pd.DataFrame(list(conso.items()), columns=["year", "value"])
fig = px.line(df, x="year", y="value", markers=True)
fig.update_layout(
    xaxis=dict(
        title="Température (°C)",  
    ),
    yaxis=dict(
        title="Consommation (MW)"  
    ),
    xaxis_title_font=dict(size=18),  
    yaxis_title_font=dict(size=18),  
    xaxis_tickfont=dict(size=14),    
    yaxis_tickfont=dict(size=14),    
    legend_font=dict(size=14),
     )

# enlever les ,5 sur les année
fig.update_xaxes(type='category')
st.plotly_chart(fig, use_container_width=True)




# ====================== Titre mix energetique Nouhaila ===============================

#charger mes data
df_data_nationales = pd.read_pickle('data/Pickles/df_data_nationales.pkl')


st.title('Présentation de Mix Energetiques')

#split the year 
df_data_nationales['year']=df_data_nationales.index.year
df_data_nationales_year = df_data_nationales.groupby('year').sum().loc[:, 'Fioul':'Ech. physiques']
df_data_nationales_year=df_data_nationales_year.reset_index()

# delete the column Ech physique and add the list type energy

df_plot = df_data_nationales_year.drop('Ech. physiques', axis=1)
y=['Nucléaire','Solaire','Hydraulique','Eolien','Bioénergies','Gaz','Fioul','Charbon','Pompage'] 

#dict of color
dict_color = {"Nucléaire":"#E4A701",
              "Nucleaire":"#E4A701",
                "Solaire":"#D66B0D",
                "Hydraulique":"#2672B0",
                "Éolien":"#72CBB7",
                "Eolien":"#72CBB7",
                "Bioénergies":"#156956",
                "Bioenergies":"#156956",
                "Gaz":"#F20809",
                "Fioul":"#80549F",
                "Charbon":"#7F651A",
                "Pompage":"#0E4269"}

#firt plot : Mix of all the energy==========================================================================================================================

st.markdown("<h4 style='text-align: center; color: black;'>les sources énergetique de France entre 2012 à 2018 </h4>", unsafe_allow_html=True)

fig = go.Figure()

for col in y:
    fig.add_trace(go.Scatter(
        x=df_plot['year'],
        y=df_plot[col],
        mode='lines',
        name=col,
        line=dict(color=dict_color[col]),
        marker=dict(size=10) 
        #fill='tozeroy'  # remplit vers l'axe 0, ce qui gère bien les valeurs négatives
    ))

fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=60, r=60, t=60, b=60),
    legend=dict(
        title="Sources d'énergie",
        bordercolor='Black',        
        borderwidth=1,
        font=dict(size=12,color='black')),

    xaxis_title=dict(text='Année',
                     font=dict(size=15)),
    yaxis_title=dict(text='Production (MW)',
                     font=dict(size=15)),
   
    #hovermode='x unified'
)

st.write(fig)

#second plot : Mix of all the energy without Nucl========================================================================================================================
st.markdown("<h4 style='text-align: center; color: black;'>les sources énergetique de France entre 2012 à 2018 Sans Nucléaire </h4>", unsafe_allow_html=True)

# deuxieme dessin sans Nucleaire
df_plot_sans_nucleaire=df_plot.drop('Nucléaire',axis=1)

#df_plot_sans_nucleaire=df_plot_sans_nucleaire.set_index('year')
y=['Solaire','Hydraulique','Eolien','Bioénergies','Gaz','Fioul','Charbon','Pompage'] 

fig = go.Figure()

for col in y:
    fig.add_trace(go.Scatter(
        x=df_plot_sans_nucleaire['year'],
        y=df_plot_sans_nucleaire[col],
        mode='lines',
        name=col,
        line=dict(color=dict_color[col]),
        marker=dict(size=10) 
        #fill='tozeroy'  # remplit vers l'axe 0, ce qui gère bien les valeurs négatives
    ))

fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=60, r=60, t=60, b=60),
    legend=dict(
        title="Sources d'énergie",
        bordercolor='Black',        
        borderwidth=1,
        font=dict(size=12,color='black')),

    xaxis_title=dict(text='Année',
                     font=dict(size=15)),
    yaxis_title=dict(text='Production (MW)',
                     font=dict(size=15)),
   
    #hovermode='x unified'
)

st.write(fig)

#3 plot : Mix avec reference===========================================================================================================


# 3 dessin Evolution de different energie en fct d'un reference d'une annee


st.markdown("<h4 style='text-align: center; color: black;'>l'évolution des sources énergetique par rapport à l'année 2012 </h4>", unsafe_allow_html=True)

ref_2012=df_plot[df_plot['year']==2012].iloc[0]
enrgy=[col for col in df_plot.columns if col !='year']
for col in enrgy:
    df_plot[col+'_diff']=(df_plot[col])*100/ref_2012[col]

fig=go.Figure()


for col in enrgy:
    #trace_color = color_map.get(col, 'black')
    fig.add_trace(go.Scatter(
        x=df_plot['year'],
        y=df_plot[col + '_diff'],
        mode='lines+markers',
        name=col,
        line=dict(color=dict_color[col])
    ))

fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=60, r=60, t=60, b=60),
    legend=dict(
        title="Sources d'énergie",
        bordercolor='Black',        
        borderwidth=1,
        font=dict(size=12,color='black')),

    xaxis_title=dict(text='Année',
                     font=dict(size=15)),
    yaxis_title=dict(text='Production (%)',
                     font=dict(size=15)),
   
    #hovermode='x unified'
)


st.write(fig)





################################################
#     #
 #   #     ##    #    #     #    ######  #####
  # #     #  #   #    #     #    #       #    #
   #     #    #  #    #     #    #####   #    #
  # #    ######  #    #     #    #       #####
 #   #   #    #   #  #      #    #       #   #
#     #  #    #    ##       #    ######  #    #
################################################





# --------------------------------------------------------------------------------------------------
# Import des données

path_to_pickles = './data/Pickles'
df_data_nationales = pd.read_pickle(path_to_pickles + '/df_data_nationales_2012-23_xb.pkl')

# --------------------------------------------------------------------------------------------------
# Dictionnaire des couleurs : 

dict_color = {"Nucléaire":"#e4a701",
              "Nucleaire":"#e4a701",
              "Solaire":"#d66b0d",
              "Hydraulique":"#2672b0",
              "Éolien":"#72cbb7",
              "Eolien":"#72cbb7",
              "Bioénergies":"#156956",
              "Bioenergies":"#156956",
              "Gaz":"#f20809",
              "Fioul":"#80549f",
              "Charbon":"#7f651a",
              "Pompage":"#0e4269"}


# ==================================================================================================
# ==================================================================================================
# ==================================================================================================

# --------------------------------------------------------------------------------------------------

# Dictionnaires des couleurs pour les fills
fill_opacity = 0.2
dict_fill_color = dict((key, label_rgb(hex_to_rgb(color)).replace("rgb","rgba").replace(")",f", {fill_opacity})")) for key, color in dict_color.items())

# Dictionnaires des couleurs pour les textes
mix = 0.8
dict_text_color = dict((key, label_rgb( [ round(mix*v) for v in  hex_to_rgb(color) ] )) for key, color in dict_color.items())

# --------------------------------------------------------------------------------------------------

# Pré-traitement des données :

# Resample à l'échelle de l'année
conso_nat = pd.DataFrame(df_data_nationales.dropna(axis=0).resample('YE').mean())
# Reindex en année
conso_nat.index = conso_nat.index.year
conso_nat.index.name = "Année"
# On veut la consommation en TWh
conso_nat = conso_nat*1e6 * 365.25*24 / 1e12  # [MW] moyen --> TWh total 

# ==================================================================================================
# ==================================================================================================
# ==================================================================================================
annee_dispo = conso_nat.index.tolist()

# Streamlit :

st.header("Évolution de la production d'électricité par filière")

annee_1 = st.selectbox(
    "Année 1",
    annee_dispo,
    index=0,
    placeholder="Sélectionner l'année 1",
    accept_new_options=False,
)

annee_2 = st.selectbox(
    "Année 2",
    annee_dispo,
    index=len(annee_dispo)-1,
    placeholder="Sélectionner l'année 1",
    accept_new_options=False,
)

cutoff = st.checkbox("Zoom", value=True)

fig, warnings = plot_mix_evolution_between(annee_1, annee_2, conso_nat, dict_color, dict_fill_color, dict_text_color, cutoff=cutoff)

st.write(fig)

if warnings is not None :
    for ligne in warnings :
        st.write(ligne)





#     #
 #   #    ####     ##    #    #  #    #
  # #    #    #   #  #   ##   #  ##   #
   #     #    #  #    #  # #  #  # #  #
   #     #    #  ######  #  # #  #  # #
   #     #    #  #    #  #   ##  #   ##
   #      ####   #    #  #    #  #    #



df_eolien = pd.read_pickle('data/Pickles/df_eolien_norm.pkl')
df_solaire = pd.read_pickle('data/Pickles/df_solaire_norm.pkl')
df_nat = pd.read_pickle("data/Pickles/df_data_nationales_2012-23.pkl")

def add_data_to_figure(fig, x, y, label="no label", color="red", line_width=1, opacity=1):
    
    fig.add_trace(
        go.Scatter(
            x=x, y=y, 
            mode='lines', # try only lines and you'll see that lasso and box select dissapear when there are too many datapoints
            name=label,
            line=dict(color=color, width=line_width),
            connectgaps=True,
            opacity=opacity
    ))

    return fig



# -----------------------------------------------------------------------------
# ---------------- L'EOLIEN DOMINE EN HIVER, LE SOLAIRE EN ETE ----------------
# -----------------------------------------------------------------------------



# df eolien solaire
df = (
    df_nat
    .loc[:, ["Eolien", "Solaire"]]
    .resample('d')
    .mean()
    .rename(columns = {"Eolien": "eolien", "Solaire": "solaire"})
)

# df line rolling window
df_line = df.copy()

rolling_window = 100
df_line['smoothed_eolien'] = df_line.eolien.rolling(rolling_window, center=True).mean()
df_line['smoothed_solaire'] = df_line.solaire.rolling(rolling_window, center=True).mean()
df_line.dropna(inplace=True)
df_line["unsmoothed_sum"] = df_line[["eolien", "solaire"]].sum(axis=1)
df_line["smoothed_sum"] = df_line[["smoothed_eolien", "smoothed_solaire"]].sum(axis=1)

# fonts dict
font = {
    'family': "Arial",
    'size': {
        'small': 12,
        'medium': 16,
        'big': 20
        },
    'color': {
        'axes': 'rgb(180, 180, 180)',
        'title': 'grey',
        'primary': 'lightcoral',
        'secondary': 'lightsteelblue',
        'highlight': 'violet'
    },
    'line width': 1.5
}

# define traces
x = df_line.index

# trace 1: eolien
y1 = df_line.eolien
label = 'Production Eolienne'
color = font['color']['secondary']
lw = font['line width']
opacity = 0.3
plot_args1 = (x, y1, label, color, lw, opacity)

# trace 2: solaire
y2 = df_line.solaire
label = 'Production Solaire'
color = font['color']['primary']
lw = font['line width']
opacity = 0.3
plot_args2 = (x, y2, label, color, lw, opacity)

# trace 3: eolien - smoothed
y3 = df_line.smoothed_eolien
label = 'Production Eolienne lissée'
color = font['color']['secondary']
lw = font['line width'] + 2.5
plot_args3 = (x, y3, label, color, lw)

# trace 4: solaire - smoothed
y4 = df_line.smoothed_solaire
label = "Production Solaire lissée"
color = font['color']['primary']
lw = font['line width'] + 2.5
plot_args4 = (x, y4, label, color, lw)

# trace 5: sum - smoothed
y5 = df_line.smoothed_sum
label = "Production Eolienne + Solaire lissée"
color = font['color']['highlight']
lw = font['line width'] + 3.5
plot_args5 = (x, y5, label, color, lw)

# draw plot
fig = go.FigureWidget()

add_data_to_figure(fig, *plot_args1)
add_data_to_figure(fig, *plot_args2)
add_data_to_figure(fig, *plot_args3)
add_data_to_figure(fig, *plot_args4)
add_data_to_figure(fig, *plot_args5)
# fig.add_hline(y=500, line_width = 2, line_dash = "dash", line_color = "grey")

custom_dates = ["2013-01-01", "2014-01-01", "2015-01-01", "2016-01-01", "2017-01-01", "2018-01-01", 
                 "2019-01-01", "2020-01-01", "2021-01-01", "2022-01-01", "2023-01-01", "2024-01-01"]
custom_years = [date[:4] for date in custom_dates]  # Extracting only the year from the dates

fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)',
                  xaxis_range=[datetime.datetime(2012, 1, 1),
                               datetime.datetime(2026, 5, 1)],
                    xaxis=dict(
                        tickvals=custom_dates,
                        ticktext=custom_years
                    ),
                  yaxis=dict(
                      title=dict(
                          text = "Production électrique (MW)"
                      )
                  ),
                  width=1400,
                  showlegend=False)

fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="#E6E6E6")

# add a title (used to describe the figure)
fig.add_annotation(dict(xref='paper', yref='paper',
                        x=0.5, y=1.10,
                        xanchor='center', yanchor='bottom',
                        text="L'éolien domine en hiver, le solaire en été",
                        font=dict(family=font["family"],
                                  size=font["size"]["big"],
                                  color=font["color"]['title']),
                        showarrow=False))

# label eolien
x, y, label, color, _ = plot_args3
fig.add_annotation(
    xref='x', yref='y',
    x=x[-1] + pd.offsets.Day(20),
    y=y.iloc[-1]-1000,
    xanchor='left', yanchor='middle',
    text="Production<br>Eolienne",                        
    font=dict(family=font["family"],size=font["size"]["big"],color=color),
    showarrow=False
    )

# label solaire
x, y, label, color, _ = plot_args4
fig.add_annotation(
    xref='x', yref='y',
    x=x[-1] + pd.offsets.Day(20),
    y=y.iloc[-1]+1000,
    xanchor='left', yanchor='middle',
    text="Production<br>Solaire",                        
    font=dict(family=font["family"],size=font["size"]["big"],color=color),
    showarrow=False
    )

# label eolien+solaire
x, y, label, color, _ = plot_args5
fig.add_annotation(
    xref='x', yref='y',
    x=x[-1] + pd.offsets.Day(20),
    y=y.iloc[-1]+1000,
    xanchor='left', yanchor='middle',
    text="Production<br>combinée",                        
    font=dict(family=font["family"],size=font["size"]["big"],color=color),
    showarrow=False
    )

# set page to large
# st.set_page_config(layout="wide")
# draw
st.plotly_chart(fig)



# -----------------------------------------------------------------------------
# ------------------ LA COMPLEMENTARITE COMPORTE DES FAILLES ------------------
# -----------------------------------------------------------------------------



# gets n days below 1000mw
n_day_under_1000mw = df_line.query("unsmoothed_sum < 1000").shape[0]

# define new trace
# trace 6: sum - unsmoothed
y6 = df_line.unsmoothed_sum
label = "Production Eolienne + Solaire non lissée"
color = font['color']['highlight']
lw = font['line width'] + 0.5
opacity = 0.3
plot_args6 = (x, y6, label, color, lw, opacity)

# create trace
fig = go.FigureWidget()

add_data_to_figure(fig, *plot_args5)
add_data_to_figure(fig, *plot_args6)
fig.add_hline(y=1000, line_width = 2, line_dash = "dash", line_color = "grey")
# fig.add_hrect(y0=500, y1=1000, line_width = 0, fillcolor = "tomato", opacity = 0.5)

fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)',
                  xaxis_range=[datetime.datetime(2012, 1, 1),
                               datetime.datetime(2026, 5, 1)],
                    xaxis=dict(
                        tickvals=custom_dates,
                        ticktext=custom_years
                    ),
                  yaxis=dict(
                      title=dict(
                          text = "Production électrique (MW)"
                      )
                  ),
                  showlegend=False)

fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="#E6E6E6")

# add a title (used to describe the figure)
fig.add_annotation(dict(xref='paper', yref='paper',
                        x=0.5, y=1.10,
                        xanchor='center', yanchor='bottom',
                        text="La complémentarité Éolien-Solaire comporte des failles...",
                        font=dict(family=font["family"],
                                  size=font["size"]["big"],
                                  color=font["color"]['title']),
                        showarrow=False))

fig.add_annotation(
    x='2012-11-14', # we take one day before just for rending, but it is the 2012-11-15
    y=507 - 10,
    text=f'15/11/2012 : 507 MW',
    yanchor='top',
    showarrow=True,
    arrowhead=1,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="tomato",
    ax=-5,
    ay=3,
    font=dict(size=12, color="tomato", family="Courier New, monospace"),
    align="left"
)

fig.add_annotation(
    x='2016-12-31', # we take one day before just for rending, but it is the 2016-12-31
    y=619 - 10,
    text=f'31/12/2016 : 619 MW',
    yanchor='top',
    showarrow=True,
    arrowhead=1,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="tomato",
    ax=-5,
    ay=4,
    font=dict(size=12, color="tomato", family="Courier New, monospace"),
    align="left"
)

fig.add_annotation(
    x='2021-01-05', # we take one day before just for rending, but it is the 2021-01-06
    y=1343 - 10,
    text=f'06/01/2021 : 1343 MW',
    yanchor='top',
    showarrow=True,
    arrowhead=1,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="tomato",
    ax=-5,
    ay=15,
    font=dict(size=12, color="tomato", family="Courier New, monospace"),
    align="left"
)

fig.add_annotation(
    xref = "paper",
    x=0.85,
    y=-500,
    text=f'{n_day_under_1000mw} Jours < 1000 MW',
    yanchor='bottom',
    # showarrow=True,
    arrowhead=1,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor="#636363",
    # ax=20,
    # ay=-200,
    font=dict(size=12, color="grey", family="Courier New, monospace"),
    align="left",
    showarrow=False
)

# label eolien+solaire
x, y, label, color, _ = plot_args5
fig.add_annotation(
    xref='x', yref='y',
    x=x[-1] + pd.offsets.Day(20),
    y=y.iloc[-1],
    xanchor='left', yanchor='middle',
    text="Production<br>combinée",                        
    font=dict(family=font["family"],size=font["size"]["big"],color=color),
    showarrow=False
    )

# draw
st.plotly_chart(fig)


# -----------------------------------------------------------------------------
# --------------- LA (NON-)COMPLEMENTARITE DES REGIMES DE VENT ----------------
# -----------------------------------------------------------------------------


# df
df_line = (
    df_eolien
    .assign(oceanique = lambda df: df["Bretagne"] + df["Centre-Val de Loire"] + df["Pays-de-la-Loire"] + df["Nouvelle-Aquitaine"] + df["Normandie"],
            continental = lambda df: df["Grand-Est"] + df["Bourgogne-Franche-Comté"] + df["Ile-de-France"] + df["Hauts-de-France"],
            mediterraneen = lambda df: df["PACA"] + df["Occitanie"] + df["Auvergne-Rhône-Alpes"])
    .loc[:, ["oceanique", "continental", "mediterraneen"]]
    .resample('d')
    .mean()
)
rolling_window = 100
df_line['smoothed_oceanique'] = df_line.oceanique.rolling(rolling_window, center=True).mean()
df_line['smoothed_continental'] = df_line.continental.rolling(rolling_window, center=True).mean()
df_line['smoothed_mediterraneen'] = df_line.mediterraneen.rolling(rolling_window, center=True).mean()
df_line.dropna(inplace=True)
df_line["smoothed_sum"] = df_line[["smoothed_oceanique", "smoothed_continental", "smoothed_mediterraneen"]].sum(axis=1)

# fonts
font = {
    'family': "Arial",
    'size': {
        'small': 12,
        'medium': 16,
        'big': 20
        },
    'color': {
        'axes': 'rgb(180, 180, 180)',
        'title': 'grey',
        'primary': 'cornflowerblue',
        'secondary': 'darkseagreen',
        'tertiary': 'crimson',
        "highlight": "grey"
    },
    'line width': 1.5
}

# define traces
x = df_line.index

# trace 1: oceanique
y1 = df_line.oceanique
label = 'Océanique'
color = font['color']['primary']
lw = font['line width']
opacity = 0.3
plot_args1 = (x, y1, label, color, lw, opacity)

# trace 2: continental
y2 = df_line.continental
label = 'Continentale'
color = font['color']['secondary']
lw = font['line width']
opacity = 0.3
plot_args2 = (x, y2, label, color, lw, opacity)

# trace 3: mediterraneen
y3 = df_line.mediterraneen
label = 'Méditerranéenne'
color = font['color']['tertiary']
lw = font['line width']
opacity = 0.3
plot_args3 = (x, y3, label, color, lw, opacity)

# trace 4: oceanique - smoothed
y4 = df_line.smoothed_oceanique
label = 'Océanique lissée'
color = font['color']['primary']
lw = font['line width'] + 2.5
plot_args4 = (x, y4, label, color, lw)

# trace 5: continental - smoothed
y5 = df_line.smoothed_continental
label = 'Continentale lissée'
color = font['color']['secondary']
lw = font['line width'] + 2.5
plot_args5 = (x, y5, label, color, lw)

# trace 6: mediterraneen - smoothed
y6 = df_line.smoothed_mediterraneen
label = 'Méditerranéenne lissée'
color = font['color']['tertiary']
lw = font['line width'] + 2.5
plot_args6 = (x, y6, label, color, lw)

# trace 7: sum - smoothed
y7 = df_line.smoothed_sum
label = "Française lissée"
color = font['color']['highlight']
lw = font['line width'] + 3.5
plot_args7 = (x, y7, label, color, lw)

# create traces
import plotly.graph_objects as go

fig = go.FigureWidget()

add_data_to_figure(fig, *plot_args1)
add_data_to_figure(fig, *plot_args2)
add_data_to_figure(fig, *plot_args3)
add_data_to_figure(fig, *plot_args4)
add_data_to_figure(fig, *plot_args5)
add_data_to_figure(fig, *plot_args6)
add_data_to_figure(fig, *plot_args7)

fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)',
                #   title=dict(
                #       text="La (non-)complémentarité des régimes de vent"
                #   ),
                  yaxis=dict(
                      title=dict(
                          text = "Production électrique éolienne"
                      )
                  ),
                  hovermode='x unified',
                  showlegend=False)

fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="#E6E6E6")

# add a title (used to describe the figure)
fig.add_annotation(dict(xref='paper', yref='paper',
                        x=0.5, y=1.10,
                        xanchor='center', yanchor='bottom',
                        text="La (non-)complémentarité des régimes de vent",
                        font=dict(family=font["family"],
                                  size=font["size"]["big"],
                                  color=font["color"]['title']),
                        showarrow=False))

# label océanique
x, y, label, color, _ = plot_args4
fig.add_annotation(
    xref='x', yref='y',
    x=x[-1] + pd.offsets.Day(20),
    y=y.iloc[-1] + 0.1,
    xanchor='left', yanchor='middle',
    text="Océanique",                        
    font=dict(family=font["family"],size=font["size"]["big"],color=color),
    showarrow=False
    )

# label continental
x, y, label, color, _ = plot_args5
fig.add_annotation(
    xref='x', yref='y',
    x=x[-1] + pd.offsets.Day(20),
    y=y.iloc[-1],
    xanchor='left', yanchor='middle',
    text="Continental",                        
    font=dict(family=font["family"],size=font["size"]["big"],color=color),
    showarrow=False
    )

# label mediterranen
x, y, label, color, _ = plot_args6
fig.add_annotation(
    xref='x', yref='y',
    x=x[-1] + pd.offsets.Day(20),
    y=y.iloc[-1] - 0.1,
    xanchor='left', yanchor='middle',
    text="Méditerranéen",                        
    font=dict(family=font["family"],size=font["size"]["big"],color=color),
    showarrow=False
    )

# label francaise
x, y, label, color, _ = plot_args7
fig.add_annotation(
    xref='x', yref='y',
    x=x[-1] + pd.offsets.Day(20),
    y=y.iloc[-1],
    xanchor='left', yanchor='middle',
    text="France",                        
    font=dict(family=font["family"],size=font["size"]["big"],color=color),
    showarrow=False
    )

# draw
st.plotly_chart(fig)

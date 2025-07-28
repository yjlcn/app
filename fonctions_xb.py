# Auteur : Xavier BEDNAREK
# Date   : 28/07/2025
#  
# Je retrace le figure qui m'était attribué dans le notebook Xavier_Plots.ipynb
# Mais en utilisant Streamlit !
#
# A exécuter avec : streamlit run figure_xavier_the_best.py

# --------------------------------------------------------------------------------------------------
# Imports des packages 
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import hex_to_rgb
from plotly.colors import label_rgb

import streamlit as st


# Fonction de tracé du graphique
def plot_mix_evolution_between(annee_1, annee_2, conso_nat, dict_color, dict_fill_color, dict_text_color, cutoff=True) :
    # Check des arguments
    if annee_1 > annee_2 :
        (annee_1, annee_2) = (annee_2, annee_1)
    
    une_seule_annee = (annee_1 == annee_2)

    # Filtre
    if une_seule_annee :
        X = conso_nat.loc[[annee_1]]
    else :
        X = conso_nat.loc[[annee_1, annee_2]]
    X = X.drop(columns=["Consommation", "Ech. physiques"])

    # On garde le pompage de coté
    X_pompage = X[["Pompage"]]

    # Classement par type d'énergie 
    index = pd.Index(["Nucléaire", "Hydraulique", "Charbon", "Fioul", "Gaz", "Solaire", "Eolien", "Bioénergies"])
    X = X[index]

    # =========================================================================================================================  

    # Min et Max pour y (en haut)
    nuke_min = X["Nucléaire"].min()
    if cutoff :
        ymin = 0.9*nuke_min
    else :
        ymin = 0
    prod_max = X.sum(axis=1).max()
    ymax = 1.05*prod_max

    # Taille relative du graphe du bas pour indiquer qu'on a couper le bas du diagramme
    h_bas = 0.05
    h_haut = (1-h_bas)
    y_min_bas = X_pompage["Pompage"].min()
    y_max_bas = ((ymax-ymin)/h_haut) * h_bas + y_min_bas

    if not cutoff :
        ymin = y_min_bas

    # Largeur d'une barre
    if not une_seule_annee :
        w_bar = (annee_2-annee_1)/2
    else :
        w_bar = 1

    # Distance interbarre
    w_interbar = (annee_2-annee_1) - w_bar

    # Titre
    if une_seule_annee :
        titre = f"Production d'électricité par filière en {annee_1}."
    else :
        titre = f"Évolution de la production d'électricité par filière entre {annee_1} et {annee_2}."

    # =========================================================================================================================  

    # Création des subplots
    fig = make_subplots(
        rows=2, cols=1,
        vertical_spacing=0.01,
        row_heights=[h_haut, h_bas],  # Le graphique principal prend 70% de la hauteur
        shared_xaxes = True,
    )

    # =========================================================================================================================  

    # Tracé spécifique pour le pompage sur le graphique du bas
    mode = "Pompage"

    valtext=[ f"{val:.3g}"  for val in X_pompage[mode]]

    # Où tracer le pompage ? Selon le cutoff
    if cutoff :
        row_pomp = 2
    else :
        row_pomp = 1

    fig.add_trace(
        go.Bar(name=mode, x=X_pompage.index, y=X_pompage[mode], width=w_bar, marker_color=dict_color[mode], text=valtext, textfont=dict(size=15), hovertemplate=mode+' (%{x}) : %{text} TWh<extra></extra>', base=0),
        row=row_pomp, col=1
    )

    # =========================================================================================================================  

    for i, mode in enumerate(X.columns):
        # Text
        valtext=[ f"{val:.3g}"  for val in X[mode]]
        # Graphique principal (en haut) avec cutoff
        fig.add_trace(
            go.Bar(name=mode, x=X.index, y=X[mode], width=w_bar, marker_color=dict_color[mode], text=valtext, textfont=dict(size=15), hovertemplate=mode+' (%{x}) : %{text} TWh<extra></extra>'),
            row=1, col=1
        )
        if cutoff :
            # Graphique du bas pour montrer qu'on a fait un cutoff
            fig.add_trace(
                go.Bar(name=mode, x=X.index, y=X[mode], width=w_bar, showlegend=False, marker_color=dict_color[mode], hovertemplate=mode+' (%{x})<extra></extra>'),
                row=2, col=1
            )

    # =========================================================================================================================  

    # Mise à jour du layout
    fig.update_layout(
        barmode='stack',
        width=800,
        height=800,
        title_text=titre
    )

    # =========================================================================================================================  

    if not une_seule_annee :

        # Tracé des surfaces interblock et des numéro
        for i, mode in enumerate(X.columns):

            # 0 - Text
            evolution = (X.at[annee_2, mode]- X.at[annee_1, mode]) / X.at[annee_1, mode]
            sign = "+" if evolution>=0 else ""
            mytext = f"{sign}{evolution:.0%}"

            # 1 - Tracé des surfaces ----------------------------------------------
            # Calcul des hauteur des lignes
            y = [X.loc[annee_1,:mode].sum(), X.loc[annee_2,:mode].sum()]
            fig.add_trace(
                go.Scatter(x=[annee_1+w_bar/2,annee_2-w_bar/2], y=y, mode="none", showlegend=False, fillcolor=dict_fill_color[mode], fill='tonexty', hoveron="fills", hoverinfo="text", text=mode+f" {mytext} (entre {annee_1} et {annee_2})"),
                row=1, col=1
            )

            if cutoff :
                # On le fait aussi sur l'autre plot
                fig.add_trace(
                    go.Scatter(x=[annee_1+w_bar/2,annee_2-w_bar/2], y=y, mode="none", showlegend=False, fillcolor=dict_fill_color[mode], fill='tonexty', hoverinfo="none"),
                    row=2, col=1
                )

            # 2 : Tracé des pourcentages ----------------------------------------------
            # Calcul des hauteur du text :
            y_1 = (X.iloc[0,:(i+1)].sum() + X.iloc[1,:(i+1)].sum())/2 # milieu de la ligne haute
            y_2 = max((X.iloc[0,:i].sum() + X.iloc[1,:i].sum())/2, ymin) # milieu de la ligne basse
            y_m = (y_1+y_2)/2 # Position finale : milieu des deux précédent
            # Décallage des text pour mieux les voir ?
            # x_shift = (2*(i%2)-1) * w_interbar * 0.1 if i > 4 else 0
            x_shift = 0

            fig.add_trace(
                go.Scatter(x=[(annee_1+annee_2)/2+x_shift], y=[y_m], text=[mytext], mode="text", textfont=dict(color=dict_text_color[mode], size=15), textposition="middle center", showlegend=False, zorder=1, hoverinfo="none"), # zorder pour pas que le fill to nexty y d'y arrete !
                row=1, col=1
            )

        # =========================================================================================================================  

        # Tracé spécifique pour le pompage sur le graphique du bas
        mode = "Pompage"

        # 0 - Text
        evolution = (abs(X_pompage.at[annee_2, mode])- abs(X_pompage.at[annee_1, mode])) / abs(X_pompage.at[annee_1, mode])
        sign = "+" if evolution>=0 else ""
        mytext = f"{sign}{evolution:.0%}"

        # 1 - Tracé des surfaces ----------------------------------------------
        # Calcul des hauteur des lignes
        y = [X_pompage.loc[annee_1,mode], X_pompage.loc[annee_2,mode]]
        fig.add_trace(
            go.Scatter(x=[annee_1+w_bar/2,annee_2-w_bar/2], y=y, mode="none", showlegend=False, fillcolor=dict_fill_color[mode], fill='tozeroy', hoveron="fills", hoverinfo="text", text=mode+f" {mytext} (entre {annee_1} et {annee_2})"),
            row=row_pomp, col=1
        )

        # 2 : Tracé des pourcentages ----------------------------------------------
        # Calcul des hauteur du text :
        y_1 = 0 # milieu de la ligne haute
        y_2 = (y[0] + y[1])/2 # milieu de la ligne basse
        y_m = (y_1+y_2)/2 # Position finale : milieu des deux précédent
        fig.add_trace(
            go.Scatter(x=[(annee_1+annee_2)/2], y=[y_m], text=[mytext], mode="text", textfont=dict(color=dict_text_color[mode], size=15), textposition="middle center", showlegend=False, zorder=1, hoverinfo="none"),
            row=row_pomp, col=1
        )

    # =========================================================================================================================  

    # Axes du graphique principal (en haut)
    if une_seule_annee :
        fig.update_xaxes(row=1, col=1, showticklabels=False, tickmode = 'array', tickvals=[annee_1], range=[annee_1-2*w_bar, annee_1+2*w_bar])
    else :
        fig.update_xaxes(row=1, col=1, showticklabels=False, tickmode = 'array', tickvals = [annee_1, annee_2])
    fig.update_yaxes(range=[ymin, ymax], title_text="Production [TWh]", row=1, col=1, gridcolor='LightGrey', zerolinecolor='black')

    # Axes du graphique de référence (en bas)
    if une_seule_annee :
        fig.update_xaxes(title_text="Année", row=2, col=1, tickmode = 'array', tickvals=[annee_1], range=[annee_1-2*w_bar, annee_1+2*w_bar])
    else :
        fig.update_xaxes(title_text="Année", row=2, col=1, tickmode = 'array', tickvals = [annee_1, annee_2])
    fig.update_yaxes(range=[y_min_bas, y_max_bas], row=2, col=1, gridcolor='LightGrey', zerolinecolor='black')

    fig.update_layout(plot_bgcolor="white")

    # =========================================================================================================================  

    if cutoff :
        warnings = ["⚠️ Attention à l'échelle !", "* La représentation de la production nucléaire à été amputée pour une meilleure visualisation."]
    else :
        warnings = None

    return fig, warnings
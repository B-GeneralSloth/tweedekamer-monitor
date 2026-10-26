# Dashboard

import streamlit as st
import pandas as pd
import plotly.express as px

# Pagina-instellingen
st.set_page_config(
    page_title="Tweede Kamer Dashboard",
    page_icon="📊",
    layout="wide"
)

# Titel
st.title("De levenscyclus van een zaak")
st.write("Hier zijn vooral gegevens te vinden over de soorten zaken die het meest worden afgewezen of niet worden afgedaan. Daarnaast wordt hier ook gekeken naar getallen en percentages en worden die vergeleken. En tot slot wordt er weergegeven welke soorten zaken het meeste voorrang krijgen.")

# CSV-bestand inlezen
df = pd.read_csv("zaken.csv")


# Grafiek "soorten zaken die het meest zijn afgedaan"
afgedaanTrue = df[df["afgedaan"] == True]

top3 = (
    afgedaanTrue["soort"]
    .value_counts()
    .head(3)
    .rename_axis("Soort zaak")
    .reset_index(name="Aantal afgedaan")
)

totaal = df["soort"].value_counts().rename("Totaal aantal")

top3["Totaal aantal"] = top3["Soort zaak"].map(totaal)

fig = px.bar(
    top3,
    x="Soort zaak",
    y=["Aantal afgedaan", "Totaal aantal"],
    barmode="group",
    title="Soorten zaken die het meest zijn afgedaan",
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)


# Grafiek "Percentages"

afgedaanTrue = df[df["afgedaan"] == True]

afgedaan = (
    afgedaanTrue["soort"]
    .value_counts()
    .rename("Aantal afgedaan")
)

totaal = df["soort"].value_counts().rename("Totaal aantal")

gegevens = pd.concat([afgedaan, totaal], axis=1).fillna(0)

gegevens["Percentage niet afgedaan"] = (
    100 - gegevens["Aantal afgedaan"] / gegevens["Totaal aantal"] * 100
).round(1)

gegevens = gegevens.reset_index(names="Soort zaak")

minimaal = st.number_input(
    "Selecteer minimaal totaal aantal zaken",
    min_value=1,
    max_value=int(gegevens["Totaal aantal"].max()),
    value=100,
    step=10
)

gegevens = gegevens[
    gegevens["Totaal aantal"] >= minimaal
]

gegevens = gegevens.sort_values(
    "Percentage niet afgedaan",
    ascending=False
).head(5)

fig = px.bar(
    gegevens,
    x="Soort zaak",
    y=["Aantal afgedaan", "Percentage niet afgedaan"],
    barmode="group",
    title="Top 5 soorten zaken met het hoogste afwijzingspercentage (van laag naar hoog)",
    labels={
        "value": "Aantal / percentage",
        "variable": "Maatstaf",
        "Soort zaak": "Soort zaak"
    },
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

# Grafiek "Voorrang"

afgedaanTrue = df[df["afgedaan"] == True]

afgedaan = (
    afgedaanTrue["soort"]
    .value_counts()
    .rename("Aantal afgedaan")
)

totaal = df["soort"].value_counts().rename("Totaal aantal")

gegevens = pd.concat([afgedaan, totaal], axis=1).fillna(0)

gegevens["Percentage niet afgedaan"] = (
    100 - gegevens["Aantal afgedaan"] / gegevens["Totaal aantal"] * 100
).round(1)

gegevens = gegevens.reset_index(names="Soort zaak")

minimaal = st.number_input(
    "Selecteer minimaal totaal aantal zaken.",
    min_value=1,
    max_value=int(gegevens["Totaal aantal"].max()),
    value=100,
    step=10
)

gegevens = gegevens[
    gegevens["Totaal aantal"] >= minimaal
]

gegevens = gegevens.sort_values(
    "Percentage niet afgedaan",
    ascending=True
).head(15)

fig = px.bar(
    gegevens,
    x="Soort zaak",
    y=["Aantal afgedaan", "Percentage niet afgedaan"],
    barmode="group",
    title="Top 15 soorten zaken met het laagste afwijzingspercentage (van laag naar hoog)",
    labels={
        "value": "Aantal / percentage",
        "variable": "Maatstaf",
        "Soort zaak": "Soort zaak"
    },
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)


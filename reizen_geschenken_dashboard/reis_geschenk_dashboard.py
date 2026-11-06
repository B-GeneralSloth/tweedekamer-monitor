# Reizen en Geschenken Dashboard via Streamlit

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

reis_df = pd.read_csv("C:/Users/maxma/Desktop/BI TK/tweedekamer-monitor/reizen_geschenken_dashboard/gold_fact_reis.csv")
geschenk_df = pd.read_csv("C:/Users/maxma/Desktop/BI TK/tweedekamer-monitor/reizen_geschenken_dashboard/gold_fact_geschenk.csv")

# rijen met negatieve reisduren verwijderen
reis_df = reis_df[reis_df.reisduur >= 0]

# roepnaam en achternaam combineren
geschenk_df["volledige_naam"] = geschenk_df.roepnaam + " " + geschenk_df.achternaam
reis_df["volledige_naam"] = reis_df.roepnaam + " " + reis_df.achternaam

# jaar toevoegen

geschenk_df["jaar"] = geschenk_df.datum.str[0:4]
reis_df["jaar"] = reis_df.van.str[0:4]

# a = geschenk_df.datum.str[0:4]
# print(a)

min_value = max(min(reis_df["jaar"]), min(geschenk_df["jaar"]))
max_value = min(max(reis_df["jaar"]), max(geschenk_df["jaar"]))
# max van min en min van max stopt out of range filters


# filter op jaar:

jaar_lijst = []
for i in range(int(min_value), int(max_value) + 1):
	jaar_lijst.append(i)
	
jaar_sidebar = st.sidebar.selectbox("Jaar", ["Alle"] + jaar_lijst)
if jaar_sidebar != "Alle": 
	geschenk_df = geschenk_df[geschenk_df["jaar"] == str(jaar_sidebar)]
	reis_df = reis_df[reis_df["jaar"] == str(jaar_sidebar)]
    
# filter op van datum:
# min_date = min(reis_df.van)
# max_date = max(reis_df.van)

# sd = datetime.strptime(min_date, "%Y-%m-%d").date()
# ed = datetime.strptime(max_date, "%Y-%m-%d").date()

# van_datum = []

# while sd <= ed:
#    van_datum.append(sd)
#    sd += timedelta(days=1)

#van_datum_sidebar = st.sidebar.selectbox("Van datum", ["Alle"] + van_datum)
#if van_datum_sidebar != "Alle": 
#    reis_df = reis_df[reis_df["van"] >= str(van_datum_sidebar)]

# filter op tot datum:

# min_date = min(reis_df.tot_en_met)
# max_date = max(reis_df.tot_en_met)

# sd = datetime.strptime(min_date, "%Y-%m-%d").date()
# ed = datetime.strptime(max_date, "%Y-%m-%d").date()

# tot_en_met_datum = []

# while sd <= ed:
#    tot_en_met_datum.append(sd)
#    sd += timedelta(days=1)

# tot_en_met_datum_sidebar = st.sidebar.selectbox("Tot datum", ["Alle"] + tot_en_met_datum)
# if tot_en_met_datum_sidebar != "Alle": 
#    reis_df = reis_df[reis_df["van"] >= str(tot_en_met_datum_sidebar)]


st.set_page_config(page_title="Reizen & Geschenken · Tweede Kamer Monitor", page_icon=":material/account_balance:", layout="wide")

st.title("Reizen en Geschenken")
st.write("Geregistreerde buitenlandse reizen en geschenken van Kamerleden.")

# 4 cards, 2 reizen, 2 geschenken
columns = st.columns(4)

# Totaal aantal reizen
columns[0].metric("Totaal aantal reizen", len(reis_df))

# Gemiddelde reisduur
columns[1].metric("Gemiddelde reisduur", round(reis_df.reisduur.mean(), 2))

# Aantal geschenken
columns[2].metric("Totaal aantal geschenken", len(geschenk_df))

# Persoon meeste geschenken
personen_geschenken = geschenk_df.volledige_naam.value_counts()
personen_geschenken_top = personen_geschenken.index.tolist()[0]
personen_geschenken_top_value = personen_geschenken.iloc[0]
columns[3].metric("Persoon meeste geschenken ontvangen", personen_geschenken_top, personen_geschenken_top_value)


#------------------------------------------------------------------------------------------------
st.divider()

# left:
bestemming_counts = reis_df.bestemming.value_counts()
bestemming_counts_top_5 = bestemming_counts.index.tolist()[0:5]
bestemming_counts_top_5_values = bestemming_counts.iloc[0:5]


# right:
partij_reizen = reis_df.fractielabel.value_counts()
partij_reizen_partijen = partij_reizen.index.tolist()
partij_reizen_values = partij_reizen.loc[partij_reizen_partijen]

fig = px.pie(names = partij_reizen_partijen, values = partij_reizen_values)



left, right = st.columns([1, 1.2])
with left:
    st.subheader("Bestemmingen")
    st.bar_chart(
        {
            "Bestemming": bestemming_counts_top_5,
            "Reizen": bestemming_counts_top_5_values,
        },
        x="Bestemming",
        y="Reizen",
        color="#18836b",
        horizontal=True,
    )
with right:
    st.subheader("Partij reizen")
    st.plotly_chart(fig)

#--------------------------------------------------------------------------
st.divider()

# left 2:
partij_geschenken = geschenk_df.afkorting.value_counts()
partij_geschenken_top_5 = partij_geschenken.index.tolist()[0:5]
partij_geschenken_top_5_values = partij_geschenken.iloc[0:5]

# right 2:
geschenk_df_date_desc = geschenk_df.sort_values(by='datum', ascending=False)
geschenk_df_right_2 = geschenk_df_date_desc[["volledige_naam", "omschrijving", "datum"]]
# print(geschenk_df_date_desc.datum)
    
left2, right2 = st.columns([1, 1.2])
with left2:
    st.subheader("Top 5 partijen aantal geschenken")
    st.bar_chart(
        {
            "Partijen": partij_geschenken_top_5,
            "Aantal geschenken": partij_geschenken_top_5_values,
        },
        x="Partijen",
        y="Aantal geschenken",
        color="#18836b",
        horizontal=False,
    )
with right2:
    st.subheader("Recente geschenk registraties")
    st.table(geschenk_df_right_2[0:5], hide_index = True)

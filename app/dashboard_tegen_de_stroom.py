from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="Tweede Kamer Monitor", layout="wide")


@st.cache_data
def laad(naam):
    return pd.read_csv(DATA / f"{naam}.csv")


# 1. Data inlezen
stemmen = laad("fact_stemming")
fracties = laad("dim_fractie")
stemmen["datum"] = pd.to_datetime(stemmen["datum"])

# 2. Filters in de zijbalk
st.sidebar.header("Filters")
begin = stemmen["datum"].min().date()
einde = stemmen["datum"].max().date()
periode = st.sidebar.date_input("Periode", (begin, einde), min_value=begin, max_value=einde)
if len(periode) != 2:
    st.info("Kies een begin- en einddatum.")
    st.stop()

alle_namen = sorted(fracties["naam_nl"].dropna().unique())
gekozen = st.sidebar.multiselect("Fracties", alle_namen, default=alle_namen)

# 3. Alleen fractiestemmen (geen persoon), geen vergissingen, alleen Voor/Tegen
stemmen = stemmen[
    (stemmen["datum"].dt.date >= periode[0]) & (stemmen["datum"].dt.date <= periode[1])
]
fractiestemmen = stemmen[
    stemmen["persoon_id"].isna()
    & (stemmen["vergissing"] != True)
    & stemmen["soort"].isin(["Voor", "Tegen"])
].copy()
fractiestemmen = fractiestemmen.merge(fracties[["fractie_id", "naam_nl"]], on="fractie_id")

# 4. Per besluit de meerderheid bepalen (gewogen naar fractiegrootte)
fractiestemmen["gewicht"] = fractiestemmen["fractie_grootte"].fillna(1)
gewicht = fractiestemmen.groupby(["besluit_id", "soort"])["gewicht"].sum().reset_index()
meerderheid = gewicht.sort_values("gewicht", ascending=False).drop_duplicates("besluit_id")
meerderheid = meerderheid.rename(columns={"soort": "meerderheid"})[["besluit_id", "meerderheid"]]

data = fractiestemmen.merge(meerderheid, on="besluit_id")
data["tegen_meerderheid"] = data["soort"] != data["meerderheid"]

# 5. Fractie-filter (pas na het bepalen van de meerderheid)
data = data[data["naam_nl"].isin(gekozen)]

# 6. Per partij uitrekenen
per_partij = (
    data.groupby("naam_nl")
    .agg(
        aantal_besluiten=("besluit_id", "count"),
        tegen=("tegen_meerderheid", "sum"),
        fractiegrootte=("fractie_grootte", "mean"),
    )
    .reset_index()
)
per_partij["percentage_tegen"] = (100 * per_partij["tegen"] / per_partij["aantal_besluiten"]).round(1)
per_partij = per_partij.sort_values("percentage_tegen", ascending=False)

# 7. Pagina tonen
st.title("Afwijkend stemgedrag")
st.write("Welke partijen stemmen het vaakst tegen de meerderheid in?")

kolom1, kolom2, kolom3 = st.columns(3)
kolom1.metric("Aantal besluiten", data["besluit_id"].nunique())
kolom2.metric("Aantal fractiestemmen", len(data))
if len(per_partij) > 0:
    kolom3.metric("Hoogste % tegen", f"{per_partij['percentage_tegen'].max()} %",
                  per_partij.iloc[0]["naam_nl"], delta_color="off")

links, rechts = st.columns(2)

with links:
    st.subheader("% tegen de meerderheid per partij")
    st.bar_chart(per_partij.set_index("naam_nl")["percentage_tegen"], horizontal=True)

with rechts:
    st.subheader("Fractiegrootte versus % tegen")
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(per_partij["fractiegrootte"], per_partij["percentage_tegen"])
    for _, rij in per_partij.iterrows():
        ax.annotate(rij["naam_nl"], (rij["fractiegrootte"], rij["percentage_tegen"]), fontsize=7)
    ax.set_xlabel("Gemiddelde fractiegrootte (zetels)")
    ax.set_ylabel("% tegen de meerderheid")
    st.pyplot(fig)

st.subheader("Cijfers per partij")
st.dataframe(per_partij.rename(columns={
    "naam_nl": "Partij", "aantal_besluiten": "Besluiten", "tegen": "Tegen meerderheid",
    "fractiegrootte": "Gem. fractiegrootte", "percentage_tegen": "% tegen",
}), hide_index=True)

st.caption("Bron: Tweede Kamer open data, stemmingen van 2024. Alleen fractiestemmen, vergissingen zijn weggelaten.")


personen = laad("dim_persoon")


geldig = stemmen[
    (stemmen["vergissing"] != True) & stemmen["soort"].isin(["Voor", "Tegen"])
].copy()
geldig["gewicht"] = geldig["fractie_grootte"].where(geldig["persoon_id"].isna(), 1).fillna(1)


gew = geldig.groupby(["besluit_id", "soort"])["gewicht"].sum().reset_index()
meerderheid_alle = gew.sort_values("gewicht", ascending=False).drop_duplicates("besluit_id")
meerderheid_alle = meerderheid_alle.rename(columns={"soort": "meerderheid"})[["besluit_id", "meerderheid"]]


leden = geldig[geldig["persoon_id"].notna()].merge(meerderheid_alle, on="besluit_id")
leden["tegen_meerderheid"] = leden["soort"] != leden["meerderheid"]
leden = leden.merge(fracties[["fractie_id", "naam_nl"]], on="fractie_id")
leden = leden.merge(personen[["persoon_id", "roepnaam", "achternaam"]], on="persoon_id", how="left")
leden["kamerlid"] = leden["roepnaam"].fillna("") + " " + leden["achternaam"].fillna("")
leden = leden[leden["naam_nl"].isin(gekozen)]


minimaal = st.sidebar.slider("Minimaal aantal stemmen per Kamerlid", 1, 100, 5)
per_lid = leden.groupby(["kamerlid", "naam_nl"]).agg(
    stemmen=("tegen_meerderheid", "size"), tegen=("tegen_meerderheid", "sum")
).reset_index()
per_lid = per_lid[per_lid["stemmen"] >= minimaal]
per_lid["percentage_tegen"] = (100 * per_lid["tegen"] / per_lid["stemmen"]).round(1)
per_lid = per_lid.sort_values("percentage_tegen", ascending=False)


st.divider()
st.header("Welke Kamerleden stemmen vaker tegen de meerderheid?")
st.write("Alleen stemmingen waarbij elk Kamerlid apart stemde (hoofdelijke stemmingen).")

if len(per_lid) == 0:
    st.warning("Geen Kamerleden over met deze filters. Zet de slider lager.")
else:
    links2, rechts2 = st.columns(2)
    with links2:
        st.subheader("Top 15 Kamerleden")
        top = per_lid.head(15).copy()
        top["label"] = top["kamerlid"] + " (" + top["naam_nl"] + ")"
        st.bar_chart(top.set_index("label")["percentage_tegen"], horizontal=True)
    with rechts2:
        st.subheader("Alle Kamerleden")
        st.dataframe(
            per_lid.rename(columns={
                "kamerlid": "Kamerlid", "naam_nl": "Fractie", "stemmen": "Stemmen",
                "tegen": "Tegen meerderheid", "percentage_tegen": "% tegen",
            }).style.background_gradient(subset=["% tegen"], cmap="Reds"),
            hide_index=True,
        )
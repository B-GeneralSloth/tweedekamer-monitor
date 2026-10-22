from pathlib import Path
import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parent / "data"


@st.cache_data
def laad_data():
    dossiers = pd.read_csv(DATA / "kamerstukdossier.csv")
    documenten = pd.read_csv(
        DATA / "document.csv",
        parse_dates=["datum", "datum_registratie", "datum_ontvangst"],
    )
    return dossiers, documenten


st.title("Levensduur en doorlooptijd")
st.caption("Een steekproef van 500 dossiers met al hun documenten.")

dossiers, documenten = laad_data()
documenten["doorlooptijd_dagen"] = (
    documenten["datum_ontvangst"] - documenten["datum_registratie"]
).dt.days

# Filters
jaren = sorted(documenten["vergaderjaar"].dropna().unique())
soorten = sorted(documenten["soort"].dropna().unique())
gekozen_jaren = st.sidebar.multiselect("Vergaderjaar", jaren, default=jaren)
gekozen_soorten = st.sidebar.multiselect("Soort document", soorten, default=soorten)
sluit_negatief_uit = st.sidebar.checkbox("Negatieve doorlooptijden uitsluiten", value=True)

df = documenten[
    documenten["vergaderjaar"].isin(gekozen_jaren)
    & documenten["soort"].isin(gekozen_soorten)
]
if df.empty:
    st.warning("Geen documenten voor deze selectie.")
    st.stop()

# Doorlooptijd per document
dl = df.dropna(subset=["doorlooptijd_dagen"])
if sluit_negatief_uit:
    dl = dl[dl["doorlooptijd_dagen"] >= 0]

# Looptijd per dossier: eerste tot laatste documentdatum
per_dossier = (
    df.dropna(subset=["datum"])
    .groupby("kamerstukdossier_id")["datum"]
    .agg(eerste="min", laatste="max", aantal_documenten="count")
    .reset_index()
)
per_dossier["looptijd_dagen"] = (per_dossier["laatste"] - per_dossier["eerste"]).dt.days
per_dossier = per_dossier.merge(
    dossiers, left_on="kamerstukdossier_id", right_on="id", how="left"
)

# Kengetallen
k1, k2, k3, k4 = st.columns(4)
k1.metric("Mediane looptijd dossier", f"{per_dossier['looptijd_dagen'].median():.0f} dagen")
k2.metric("Gemiddelde looptijd dossier", f"{per_dossier['looptijd_dagen'].mean():.0f} dagen")
k3.metric("Mediane doorlooptijd", f"{dl['doorlooptijd_dagen'].median():.0f} dagen")
k4.metric("Binnen 7 dagen", f"{(dl['doorlooptijd_dagen'] <= 7).mean() * 100:.0f}%")

# Grafieken
links, rechts = st.columns(2)

with links:
    st.subheader("Dossiers per looptijdcategorie")
    labels = ["1. minder dan 1 mnd", "2. 1-6 mnd", "3. 6-12 mnd", "4. 1-5 jaar", "5. meer dan 5 jaar"]
    grenzen = [-1, 30, 182, 365, 1826, float("inf")]
    categorie = pd.cut(per_dossier["looptijd_dagen"], bins=grenzen, labels=labels)
    telling = categorie.value_counts().reindex(labels).fillna(0).astype(int)
    st.bar_chart(pd.DataFrame({"aantal dossiers": telling.values}, index=labels))

with rechts:
    st.subheader("Mediane doorlooptijd per soort document")
    st.bar_chart(dl.groupby("soort")["doorlooptijd_dagen"].median())

st.subheader("Mediane doorlooptijd per jaar")
st.line_chart(dl.groupby(dl["datum_registratie"].dt.year)["doorlooptijd_dagen"].median())

st.subheader("Langstlopende dossiers")
langste = per_dossier.nlargest(10, "looptijd_dagen")[
    ["nummer", "titel", "aantal_documenten", "looptijd_dagen"]
]
st.dataframe(langste, hide_index=True)
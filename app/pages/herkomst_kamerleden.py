from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
WEERGAVE = {"'s-Gravenhage": "Den Haag", "'s-Hertogenbosch": "Den Bosch"}


@st.cache_data
def laad_data() -> pd.DataFrame:
    personen = pd.read_parquet(DATA_DIR / "personen.parquet")
    personen["geboorte_status"] = personen["plaats_status"].replace(
        {
            "gematcht (eenduidig)": "gematcht",
            "geen plaats ingevuld": "niet ingevuld",
            "niet eenduidig (meerdere gemeenten)": "niet eenduidig",
        }
    )
    return personen


personen = laad_data()
st.sidebar.header("Filters")

df = personen.copy()
if "functie" in df.columns:
    functies = sorted(df["functie"].dropna().unique())
    gekozen_functies = st.sidebar.multiselect("Functie", functies, default=functies)
    df = df[df["functie"].isin(gekozen_functies)]

decennia = personen["decennium"].dropna()
decennium_min = int(decennia.min())
decennium_max = int(decennia.max())
gekozen_decennia = st.sidebar.slider(
    "Geboortedecennium",
    decennium_min,
    decennium_max,
    (decennium_min, decennium_max),
    step=10,
)
if gekozen_decennia != (decennium_min, decennium_max):
    df = df[df["decennium"].between(*gekozen_decennia)]

niveau = st.sidebar.radio("Niveau", ["Provincie", "Gemeente"])
soort = st.sidebar.radio("Wat tonen?", ["Geboorteplaats", "Woonplaats"])
prefix = "geboorte" if soort == "Geboorteplaats" else "woon"

st.title("Waar komen Kamerleden vandaan, en waar wonen ze?")
if df.empty:
    st.warning("Geen personen binnen deze filters.")
    st.stop()

n = len(df)
n_geb = int(
    df["geboorte_status"].isin(["gematcht", "niet gevonden", "niet eenduidig"]).sum()
)
n_geb_ok = int((df["geboorte_status"] == "gematcht").sum())
n_woon = int(
    df["woon_status"].isin(["gematcht", "niet gevonden", "niet eenduidig"]).sum()
)
n_woon_ok = int((df["woon_status"] == "gematcht").sum())

kolommen = st.columns(5)
kolommen[0].metric("Personen", f"{n}")
kolommen[1].metric(
    "Geboorteplaats ingevuld",
    f"{n_geb}",
    f"{100 * n_geb / n:.0f}%",
    delta_color="off",
)
kolommen[2].metric(
    "Geboorteplaats aan gemeente gekoppeld",
    f"{n_geb_ok}",
    f"{100 * n_geb_ok / n:.0f}%",
    delta_color="off",
)
kolommen[3].metric(
    "Woonplaats ingevuld",
    f"{n_woon}",
    f"{100 * n_woon / n:.0f}%",
    delta_color="off",
)
kolommen[4].metric(
    "Woonplaats aan gemeente gekoppeld",
    f"{n_woon_ok}",
    f"{100 * n_woon_ok / n:.0f}%",
    delta_color="off",
)
st.caption(
    "Percentages zijn aandelen van alle personen binnen de filters. Voor oudere "
    "geboortejaren is geboorteplaats vaak niet vastgelegd."
)


def tel(frame: pd.DataFrame, voorvoegsel: str, niveau: str) -> pd.DataFrame:
    """Count matched people by province or municipality."""
    locatie = frame[frame[f"{voorvoegsel}_status"] == "gematcht"].copy()
    provincie = f"{voorvoegsel}_provincie"

    if niveau == "Provincie":
        telling = (
            locatie.groupby(provincie)
            .size()
            .rename("aantal")
            .reset_index()
            .rename(columns={provincie: "naam"})
        )
    else:
        gemeente = f"{voorvoegsel}_gemeente"
        gemeente_code = f"{voorvoegsel}_gemeentecode"
        telling = (
            locatie.groupby([gemeente_code, gemeente, provincie], dropna=False)
            .size()
            .rename("aantal")
            .reset_index()
        )
        telling["naam"] = telling[gemeente].replace(WEERGAVE)
        telling.loc[telling[provincie].notna(), "naam"] = (
            telling.loc[telling[provincie].notna(), gemeente]
            + " ("
            + telling.loc[telling[provincie].notna(), provincie]
            + ")"
        )

    totaal = telling["aantal"].sum()
    telling["aandeel_%"] = (100 * telling["aantal"] / totaal).round(1) if totaal else 0.0
    return telling


tab_verdeling, tab_top, tab_vergelijk, tab_status = st.tabs(
    ["Verdeling", "Top gemeenten", "Geboorte vs woon", "Matchstatus"]
)

with tab_verdeling:
    telling = tel(df, prefix, niveau)
    noemer = n_geb_ok if prefix == "geboorte" else n_woon_ok
    st.subheader(f"{soort} per {niveau.lower()} (n = {noemer} gekoppeld)")
    if telling.empty:
        st.info("Geen gekoppelde locaties binnen deze filters.")
    else:
        fig = px.bar(
            telling.sort_values("aantal"),
            x="aantal",
            y="naam",
            orientation="h",
            hover_data={"aandeel_%": True},
            labels={
                "aantal": "Personen",
                "naam": niveau,
                "aandeel_%": "Aandeel (%)",
            },
            color="aantal",
            color_continuous_scale="Blues",
        )
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis_title=None,
            height=max(450, min(900, 24 * len(telling) + 100)),
        )
        st.plotly_chart(fig, width="stretch")

with tab_top:
    aantal_top = st.slider("Aantal gemeenten", 5, 40, 15)
    kolommen = st.columns(2)
    for kolom, voorvoegsel, titel in (
        (kolommen[0], "geboorte", "Geboorteplaats"),
        (kolommen[1], "woon", "Woonplaats"),
    ):
        telling = (
            tel(df, voorvoegsel, "Gemeente")
            .nlargest(aantal_top, "aantal")
            .sort_values("aantal")
        )
        if telling.empty:
            kolom.info(f"Geen gekoppelde {titel.lower()}en.")
            continue
        fig = px.bar(
            telling,
            x="aantal",
            y="naam",
            orientation="h",
            title=titel,
            hover_data={"aandeel_%": True},
        )
        fig.update_layout(yaxis_title=None, height=120 + 24 * aantal_top)
        kolom.plotly_chart(fig, width="stretch")

with tab_vergelijk:
    beide = df[
        (df["geboorte_status"] == "gematcht") & (df["woon_status"] == "gematcht")
    ].copy()
    st.write(
        "Alleen personen met zowel een gekoppelde geboorte- als woonplaats: "
        f"**n = {len(beide)}**."
    )
    if beide.empty:
        st.info("Geen personen met beide gegevens binnen deze filters.")
    else:
        zelfde = (
            beide["geboorte_provincie"] == beide["woon_provincie"]
        ).mean()
        st.metric("Woont in dezelfde provincie als geboorte", f"{100 * zelfde:.1f}%")
        telling = pd.crosstab(
            beide["geboorte_provincie"], beide["woon_provincie"]
        )
        fig = px.imshow(
            telling,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Blues",
            labels={
                "x": "Woonprovincie",
                "y": "Geboorteprovincie",
                "color": "Personen",
            },
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Woonplaats is voor veel oud-Kamerleden niet vastgelegd en geeft niet altijd "
            "de woonplaats tijdens hun Kamerlidmaatschap."
        )

with tab_status:
    st.write(
        "Hoeveel personen vallen in welke categorie? Dit zijn de noemers achter de "
        "geografische verdelingen."
    )
    rijen = []
    for voorvoegsel, titel in (
        ("geboorte", "Geboorteplaats"),
        ("woon", "Woonplaats"),
    ):
        telling = df[f"{voorvoegsel}_status"].value_counts()
        for status, aantal in telling.items():
            rijen.append(
                {
                    "soort": titel,
                    "status": status,
                    "aantal": int(aantal),
                    "aandeel_%": round(100 * aantal / n, 1),
                }
            )
    st.dataframe(pd.DataFrame(rijen), width="stretch", hide_index=True)
    st.caption(
        "'Niet gevonden' is vooral buitenland en oude gemeenten. 'Niet eenduidig' zijn "
        "plaatsnamen die in meerdere gemeenten voorkomen."
    )

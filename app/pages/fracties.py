import streamlit as st

st.set_page_config(page_title="Fracties · Tweede Kamer Monitor", page_icon=":material/account_balance:", layout="wide")

st.title("Fracties")
st.write("Zetelverdeling en vertegenwoordiging in de Tweede Kamer. Alle cijfers op deze pagina zijn mockdata.")

columns = st.columns(3)
columns[0].metric("Fracties", "15")
columns[1].metric("Zetels", "150")
columns[2].metric("Grootste fractie", "34 zetels", "Voorbeeldfractie")

st.divider()
left, right = st.columns([1, 1.2])
with left:
    st.subheader("Zetelverdeling")
    st.bar_chart(
        {
            "Fractie": ["Fractie A", "Fractie B", "Fractie C", "Fractie D", "Fractie E", "Fractie F", "Fractie G", "Fractie H", "Fractie I", "Fractie J", "Fractie K", "Fractie L", "Fractie M", "Fractie N", "Fractie O"],
            "Zetels": [34, 25, 20, 15, 10, 8, 7, 6, 5, 4, 4, 4, 4, 4, 4],
        },
        x="Fractie",
        y="Zetels",
        color="#d5943c",
        horizontal=True,
    )
with right:
    st.subheader("Fractieoverzicht")
    st.dataframe(
        [
            {"Fractie": "Fractie A", "Zetels": 34, "Kamerleden": 34, "Wijziging dit jaar": "+1"},
            {"Fractie": "Fractie B", "Zetels": 25, "Kamerleden": 25, "Wijziging dit jaar": "0"},
            {"Fractie": "Fractie C", "Zetels": 20, "Kamerleden": 20, "Wijziging dit jaar": "-1"},
            {"Fractie": "Fractie D", "Zetels": 15, "Kamerleden": 15, "Wijziging dit jaar": "0"},
            {"Fractie": "Fractie E", "Zetels": 10, "Kamerleden": 10, "Wijziging dit jaar": "+2"},
        ],
        hide_index=True,
        width="stretch",
    )
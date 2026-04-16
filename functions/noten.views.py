import pandas as pd
import streamlit as st
from functions.noten import parse_list, weighted_average, grade_label
from utils.data_manager import DataManager
import altair as alt

st.title("Notenrechner (CH‑Skala: 6=best, 4=Bestanden)")
st.write("Noten kommasepariert eingeben. Optional Gewichte (kommasepariert). Beispiel: Noten: 5,4.5,3.5  Gewichte: 2,1,1")
st.info(
    "Hinweis: Die App speichert jede Berechnung als Eintrag und ist vor allem dafür "
    "gedacht, längerfristige Verläufe (z. B. Semester‑Gesamtdurchschnitte) zu verfolgen. "
    "Bei sehr häufigen, täglichen Einzelberechnungen entstehen viele Einträge und die "
    "Auswertung/Visualisierung verliert an Aussagekraft. Für kurzfristige Tests oder "
    "Probe‑Berechnungen ist diese App weniger geeignet.")

with st.form("noten_form"):
    grades_s = st.text_input("Noten (kommasepariert)", value="5,4.5,4")
    weights_s = st.text_input("Gewichte optional (kommasepariert)", value="")
    submit = st.form_submit_button("Berechnen")

if submit:
    grades = parse_list(grades_s)
    weights = parse_list(weights_s) if weights_s.strip() != "" else None
    
    result = weighted_average(grades, weights)

    if result["average"] is None:
        st.error("Ungültige Eingabe. Prüfe Noten/Gewichte.")
    else:
        st.subheader("Ergebnis")
        st.write(f"Durchschnitt: **{result['average']:.2f}**")
        st.write(f"Bewertung: **{result["label"]}**")
        st.write("- Hinweis: Schweizer Skala (6 = beste Note; 4 = bestanden).")

        result = {
            "timestamp": pd.Timestamp.now(),
            "grades": grades_s,
            "weights": weights_s,
            "average": round(result["average"], 2),
        }
        st.session_state["data_df"] = pd.concat(
            [st.session_state["data_df"], pd.DataFrame([result])],
            ignore_index=True,
        )
data_manager = DataManager()
data_manager.save_user_data(st.session_state['data_df'], 'data.csv')

# immer die History anzeigen
st.dataframe(st.session_state["data_df"])

if "data_df" in st.session_state and not st.session_state["data_df"].empty:
    df_plot = st.session_state["data_df"].copy()
    df_plot["timestamp"] = pd.to_datetime(df_plot["timestamp"])
    df_plot = df_plot.sort_values("timestamp")

    st.subheader("Verlauf: Durchschnittsnote")

    chart = (
        alt.Chart(df_plot)
        .mark_line(point=True)
        .encode(
            x=alt.X("timestamp:T", title="Zeit"),
            y=alt.Y("average:Q", title="Durchschnitt"),
            tooltip=["timestamp:T", "average:Q", "grades", "weights"],
        )
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
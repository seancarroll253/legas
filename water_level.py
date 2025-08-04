import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone




# ✅ Custom blue styling for main content only
def apply_custom_styles():
    st.markdown("""
        <style>
        /* Main background */
        [data-testid="stAppViewContainer"] > .main {
            background-color: #00264d;
        }

        /* Text color inside main */
        [data-testid="stAppViewContainer"] > .main * {
            color: white;
        }

        /* Input fields */
        input, textarea {
            background-color: #004080;
            color: white;
        }

        /* Buttons */
        button {
            background-color: #0059b3;
            color: white;
            border: none;
        }

        /* Plotly chart background white for contrast */
        .js-plotly-plot .plotly {
            background-color: white !important;
        }

        /* Hide Streamlit UI */
        #MainMenu, header, footer {
            visibility: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

# Station names and IDs
STATIONS = {
    2: "Alzette zu Hesper",
    6: "Eisch um Hunnebour",
    5: "Mamer zu Schoenfels",
}

@st.cache_data(ttl=300)
def fetch_data(station_id):
    url = f"https://www.inondations.lu/api/station/graph-data/{station_id}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def parse_levels(data):
    if not data or "levels" not in data:
        return pd.DataFrame()
    levels = data['levels']
    df = pd.DataFrame(levels)
    if df.empty:
        return df
    df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)
    df['level'] = df['level'].astype(float)
    return df

def show_station(station_id, name):
    data = fetch_data(station_id)
    st.subheader(f"📍 {name}")

    if "error" in data:
        st.error(f"Feeler beim lueden vun den Donnéeën (ID {station_id}): {data['error']}")
        return

    df = parse_levels(data)
    if df.empty:
        st.warning("Keng Donnéeën verfügbar.")
        return

    thresholds = data.get("thresholds", {})
    cote_prealerte = thresholds.get("cote-prealerte")
    cote_alerte = thresholds.get("cote-alerte")

    now = pd.Timestamp(datetime.now(timezone.utc))
    df_past = df[df['time'] <= now]
    df_future = df[df['time'] > now]

    # Show chart
    st.line_chart(df.set_index('time')['level'], use_container_width=True, height=200)

    # Current level
    if not df_past.empty:
        last_level = df_past['level'].iloc[-1]
        last_time = df_past['time'].iloc[-1].strftime("%d.%m.%Y %H:%M")
        level_text = f"{last_level:.1f} cm  \n🕒 {last_time}"

        if cote_alerte and last_level >= cote_alerte:
            st.error(f"🚨 **ALARM!** Aktuellen Waasserstand: {level_text}")
        elif cote_prealerte and last_level >= cote_prealerte:
            st.warning(f"⚠️ **Virwarnung:** Aktuellen Waasserstand: {level_text}")
        else:
            st.success(f"Aktuellen Waasserstand (cm): {level_text}")
    else:
        st.info("Keng rezent Miessung fonnt.")

    # Show thresholds
    if thresholds:
        st.caption(f"⚠️ Virwarnniveau: {cote_prealerte} cm &nbsp;&nbsp;&nbsp; 🚨 Alarmniveau: {cote_alerte} cm")

    # Rain forecast (placeholder)
    st.markdown("🌧️ **Reenprognos (Demo):** 3mm an den nächsten 2 Stonnen")

# Run app
def app():
    apply_custom_styles()  # ✅ First thing
    st.title("🌊 Waasserstänn (Live)")
    st.caption("🕒 Dës Säit aktualiséiert automatesch all 5 Minutten.")

    col1, col2, col3 = st.columns(3)
    with col1:
        show_station(2, STATIONS[2])
    with col2:
        show_station(6, STATIONS[6])
    with col3:
        show_station(5, STATIONS[5])

if __name__ == "__main__":
    app()

import requests
import streamlit as st
from datetime import datetime, timedelta, date
import pytz
from streamlit_autorefresh import st_autorefresh
import json
import os
from dateutil import parser



EVENTS_FILE = "events.json"
CHECKLIST_FILE = "checklist.json"


def load_checklist():
    if not os.path.exists(CHECKLIST_FILE):
        with open(CHECKLIST_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(CHECKLIST_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(CHECKLIST_FILE, "w") as f:
            json.dump([], f)
        return []

def save_checklist(items):
    with open(CHECKLIST_FILE, "w") as f:
        json.dump(items, f, indent=2)



def load_events():
    if not os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "w") as f:
            json.dump([], f)

    try:
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(EVENTS_FILE, "w") as f:
            json.dump([], f)
        return []

lux_tz = pytz.timezone("Europe/Luxembourg")

def parse_event_date(date_str):
    dt = parser.parse(date_str)
    if dt.tzinfo is None:
    
        dt = lux_tz.localize(dt)
    else:
       
        dt = dt.astimezone(lux_tz)
    return dt



# --- Cache data fetching ---
@st.cache_data(ttl=300)
def fetch_data(url, _cookies):  # underscore means Streamlit skips hashing _cookies
    resp = requests.get(url, cookies=_cookies)
    resp.raise_for_status()
    return resp.json()

def app(user=None):

    st.markdown(
    """
    <style>
        body {
            background-color: #00264d;
        }

        .stApp {
            background-color: #00264d;
        }

        .custom-box {
            background-color: #004080;
            padding: 20px;
            border-radius: 0px;
            color: white;
            width: 100%;
            margin-bottom: 20px;
            font-size: 0.85rem; /* smaller text inside the box */
        }

        .custom-box h1,
        .custom-box h2,
        .custom-box h3 {
            font-size: 1rem;  /* smaller size for headers */
            margin-bottom: 10px;
        }

        .custom-box .stCheckbox {
            color: white !important;
        }

        .custom-box .stCheckbox > div {
            background-color: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        .stMarkdown p, .stCheckbox > label, .stCheckbox > div > label {
            color: white !important;
        }

        .custom-box label {
            color: white !important;
        }

        h1, h2, h3 {
            color: white;
            margin: 0;
        }

        .status-box {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 0px;
            font-weight: bold;
            color: white;
        }

        .status-1, .status-2 {
            background-color: #28a745;
        }

        .status-3, .status-4, .status-5, .status-7, .status-8 {
            background-color: #ffc107;
        }

        .status-6 {
            background-color: #8B0000;
        }

        .crew-line {
            display: flex;
            justify-content: flex-start;
            gap: 10px;
            font-family: monospace;
            margin: 0;
            padding: 0;
            line-height: 1.1;
        }

        .position {
            width: 80px;
            text-align: left;
            font-weight: bold;
            color: #ccc;
        }

        .name {
            flex-grow: 1;
            text-align: left;
        }
    </style>
    """,
    unsafe_allow_html=True
)
    if user:
        st.sidebar.markdown(f"**Logged in as:** {user}")



    # --- Auto-refresh every 1 minute ---
    st_autorefresh(interval=60_000, limit=None, key="auto_refresh")



    # --- Vehicle icons ---
    vehicle_icons = {
        "HLF": "🚒",
        "DLK": "🚒",
        "RTW": "🚑"
    }



    # --- Vehicle URLs ---
    vehicles_urls = {
        "MerschHLF21": "https://portailcgdis.intranet.etat.lu/api/current-situation/schedules/273",
        "MerschDLK21": "https://portailcgdis.intranet.etat.lu/api/current-situation/schedules/273",
        "LintgenRTW1": "https://portailcgdis.intranet.etat.lu/api/current-situation/schedules/588",
        "LintgenRTW2": "https://portailcgdis.intranet.etat.lu/api/current-situation/schedules/588"
    }

    cookies = st.secrets.cgdis_cookies

    service_plan_names = {
        "MerschHLF21": "MERSCH-HLF21",
        "MerschDLK21": "MERSCH-DLK21",
        "LintgenRTW1": "LINTGEN-RTW1",
        "LintgenRTW2": "LINTGEN-RTW2"
    }

    vehicle_plates = {
        "MerschHLF21": "CG 2040",
        "MerschDLK21": "CG 1468",
        "LintgenRTW1": "CG 2443",
        "LintgenRTW2": "CG 1153"
    }

    OPENWEATHER_API_KEY = st.secrets.get("openweather_api_key", "181d4e4c770667b88b051a06cbe5655a")
    CITY = "Mersch"
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"

    POSITION_ORDER_HLF = {
        "Chef de Section": 1,
        "Machiniste": 2,
        "Chef Binôme 1": 3,
        "Equipier Binôme 1": 4,
        "Chef Binôme 2": 5,
        "Equipier Binôme 2": 6
    }

    POSITION_ORDER_DLK = {
        "Chef d'Agrès": 1,
        "Machiniste": 2,
        "Equipier": 3
    }

    POSITION_ORDER_RTW = {
        "Chef d'Agrès": 1,
        "Chauffeur": 2,
        "Equipier": 3
    }

    POSITION_SHORT = {
        "Chef de Section": "Ch. S.",
        "Machiniste": "Mach.",
        "Chef Binôme 1": "Ch. B.1",
        "Equipier Binôme 1": "Eq. B.1",
        "Chef Binôme 2": "Ch. B.2",
        "Equipier Binôme 2": "Eq. B.2",
        "Chef d'Agrès": "Ch. d'A.",
        "Chauffeur": "Chauf.",
        "Equipier": "Equip."
    }

    lux_weekdays = {
        0: "Méindeg",
        1: "Dënschdeg",
        2: "Mëttwoch",
        3: "Donneschdeg",
        4: "Freideg",
        5: "Samschdeg",
        6: "Sonndeg"
    }

    lux_months = {
        1: "Januar",
        2: "Februar",
        3: "Mäerz",
        4: "Abrëll",
        5: "Mee",
        6: "Juni",
        7: "Juli",
        8: "August",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Dezember"
    }

    def status_class(status):
        status_digit = str(status)[0] if str(status) and str(status)[0].isdigit() else "0"
        return f"status-{status_digit}" if status_digit in map(str, range(1, 9)) else ""

    def get_crew_list(data, service_plan_name, position_order):
        plan = next((sp for sp in data if sp.get("servicePlanName") == service_plan_name), None)
        if not plan:
            return None, None

        status = plan.get("servicePlanVehiculeStatus", {}).get("status", {}).get("value", "Unknown")
        crew_rows = []
        for row in plan.get("rows", []):
            for prestation in row.get("prestations", []):
                person = prestation.get("person", {})
                position = prestation.get("position", {}).get("label", "")
                full_name = f"{person.get('firstName', '')} {person.get('lastName', '')}".strip()
                order = position_order.get(position, 999)
                crew_rows.append((order, position, full_name))

        crew_rows.sort(key=lambda x: x[0])
        return status, crew_rows

    lux_tz = pytz.timezone("Europe/Luxembourg")
    now = datetime.now(lux_tz)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)


    # --- Header with logo ---
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1 style="color: white; margin: 0;">CIS Mersch</h1>
            <img src="https://i.postimg.cc/4y7B4JxM/logo-CGDIS.png" alt="CGDIS Logo" style="height: 60px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    weekday_lux = lux_weekdays[now.weekday()]
    month_lux = lux_months[now.month]
    date_str = f"{weekday_lux}, {now.day}. {month_lux} {now.year} - {now.strftime('%H:%M')}"

    st.markdown(
        f"""
        <div class='custom-box' style='white-space: nowrap; max-width: none; min-width: 600px;'>
            <h2 style='display: inline;'>🕒 {date_str}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )



    # --- Load events and prepare upcoming "Mutual Calendar" events ---
    all_events = load_events()
    upcoming_mutual_events = []
    allowed_calendars = ["Gemeinsam CIS Kalenner", "Batiment", "Gefierer", "Instruktiounssaal"]
    for e in all_events:
        if e.get("calendar_type") in allowed_calendars:
            start_dt = parse_event_date(e["start"])
            if start_dt >= start_of_week:
                upcoming_mutual_events.append(e)



    # --- Layout columns ---
    col_hlf, col_rtw, col_custom, col_weather = st.columns([2, 2, 3, 2])



    # --- HLF & DLK Column ---
    with col_hlf:
        for key in ["MerschHLF21", "MerschDLK21"]:
            vtype = "HLF" if "HLF" in key else "DLK"
            pos_order = POSITION_ORDER_HLF if "HLF" in key else POSITION_ORDER_DLK
            try:
                data = fetch_data(vehicles_urls[key], cookies)
                service_plan_name = service_plan_names[key]
                status, crew_list = get_crew_list(data, service_plan_name, pos_order)
                if status == "Unknown" or status is None:
                    status = 0
                status_cls = status_class(status)

                crew_html = (
                    "<br>".join(
                        f"<div class='crew-line'><span class='position'>{POSITION_SHORT.get(pos, pos)}</span><span class='name'>{name}</span></div>"
                        for _, pos, name in crew_list
                    ) if crew_list else "Keng Personal Daten"
                )

                st.markdown(
                    f"""
                    <div class='custom-box'>
                        <h3>{vehicle_icons[vtype]} {key} ({vehicle_plates[key]})
                            <span class="status-box {status_cls}">Status: {str(status)[0] if str(status) and str(status)[0].isdigit() else "?"}</span>
                        </h3>
                        {crew_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Feeler beim lueden vun den Donnéeë fir {key}: {e}")



    # --- RTW Column ---
    with col_rtw:
        for key in ["LintgenRTW1", "LintgenRTW2"]:
            vtype = "RTW"
            pos_order = POSITION_ORDER_RTW
            try:
                data = fetch_data(vehicles_urls[key], cookies)
                service_plan_name = service_plan_names[key]
                status, crew_list = get_crew_list(data, service_plan_name, pos_order)
                if status == "Unknown" or status is None:
                    status = 0
                status_cls = status_class(status)

                crew_html = (
                    "<br>".join(
                        f"<div class='crew-line'><span class='position'>{POSITION_SHORT.get(pos, pos)}</span><span class='name'>{name}</span></div>"
                        for _, pos, name in crew_list
                    ) if crew_list else "Keng Personal Daten"
                )

                st.markdown(
                    f"""
                    <div class='custom-box'>
                        <h3>{vehicle_icons[vtype]} {key} ({vehicle_plates[key]})
                            <span class="status-box {status_cls}">Status: {str(status)[0] if str(status) and str(status)[0].isdigit() else "?"}</span>
                        </h3>
                        {crew_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Feeler beim lueden vun den Donnéeë fir {key}: {e}")



# --- Upcoming Events Box ---
    with col_custom:

        html_content = "<div class='custom-box'><h2>Kalenner Entrée</h2>"

        if upcoming_mutual_events:
            for e in upcoming_mutual_events:
                start_dt = parse_event_date(e["start"])
                end_dt = parse_event_date(e["end"])
                ganzen_daag = e.get("all_day", False)

                prefix = e.get("calendar_type", "Kalender")
                extra = ""

                if prefix == "Gefierer" and e.get("vehicle"):
                    extra = f" ({e['vehicle']})"

                prefix = f"{prefix}{extra}: "

                if ganzen_daag:
                    date_str = start_dt.strftime('%d.%m.%Y')
                    display_line = f"{date_str} - Ganzen Daag"
                else:
                    display_line = f"{start_dt.strftime('%d.%m.%Y %H:%M')} - {end_dt.strftime('%d.%m.%Y %H:%M')}"

                html_content += f"• {prefix} {e['title']} {display_line}<br><br>"

        else:
            html_content += "<p>Keng Evenementer an der aktueller Woch oder spéider</p>"

        html_content += "</div>"
        st.markdown(html_content, unsafe_allow_html=True)

        # --- To do Box BELOW Upcoming Events ---
        todo_html = "<div class='custom-box'><h2>To do:</h2>"

        checklist_items = load_checklist()
        if checklist_items:
            for item in checklist_items:
                todo_html += f"<p>• {item['text']}</p>"
        else:
            todo_html += "<p><i>Keng Aufgab ze maachen.</i></p>"

        todo_html += "</div>"
        st.markdown(todo_html, unsafe_allow_html=True)



    # --- Weather Column ---
    with col_weather:
        try:
            weather_resp = requests.get(weather_url)
            weather_resp.raise_for_status()
            weather_data = weather_resp.json()

            temp = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            pressure = weather_data["main"]["pressure"]
            wind_speed = weather_data["wind"]["speed"]
            sunrise_ts = weather_data["sys"]["sunrise"]
            sunset_ts = weather_data["sys"]["sunset"]

            sunrise = datetime.fromtimestamp(sunrise_ts, lux_tz).strftime('%H:%M')
            sunset = datetime.fromtimestamp(sunset_ts, lux_tz).strftime('%H:%M')

            html_weather = f"""
            <div class='custom-box'>
                <h2>🌤️ D'Wieder zu {CITY}</h2>
                <p>Temperatur: {temp}C°</p>
                <p>Fiichtegkeet: {humidity}%</p>
                <p>Loftdrock: {pressure} hPa</p>
                <p>Wand: {wind_speed} m/s</p>
                <p>Sonnenopgang: {sunrise}</p>
                <p>Sonnenënnergang: {sunset}</p>
            </div>
            """
            st.markdown(html_weather, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Konnt d'Wiederinformatioun net lueden: {e}")

if __name__ == "__main__":
    app()





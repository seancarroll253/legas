import streamlit as st
import json
import os
from datetime import datetime, time


# --- Add CSS to match dashboard style ---
st.markdown(
    """
    <style>
    section.main {
        background-color: #00264d !important;
        color: white !important;
    }
    section.main .css-1d391kg,
    section.main .css-1offfwp,
    section.main .css-1v3fvcr,
    section.main .css-1piskbq,
    section.main .stTextInput>div>div>input,
    section.main .stTextArea>div>textarea,
    section.main .stSelectbox>div>div>div,
    section.main .stButton>button {
        color: white !important;
    }
    section.main .stTextInput>div>div>input,
    section.main .stTextArea>div>textarea {
        background-color: #004080 !important;
    }
    section.main .streamlit-expanderHeader {
        color: white !important;
        background-color: #004080 !important;
    }
    section.main .custom-box {
        background-color: #004080 !important;
        padding: 20px;
        border-radius: 0;
        color: white !important;
        margin-bottom: 15px;
    }
    section.main .custom-box h1, 
    section.main .custom-box h2, 
    section.main .custom-box h3, 
    section.main .custom-box h4 {
        color: white !important;
    }
    section.main .fc-toolbar-chunk, 
    section.main .fc-button, 
    section.main .fc-button-primary {
        background-color: #004080 !important;
        color: white !important;
    }
    section.main .fc-daygrid-day-number {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Events file location ---
EVENTS_FILE = "events.json"

# --- Load events function ---
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

# --- Save events function ---
def save_events(events):
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)

# --- Load vehicles from external JSON ---
def load_vehicles():
    vehicles_file = "vehicles.json"
    if not os.path.exists(vehicles_file):
        return []
    with open(vehicles_file, "r") as f:
        return json.load(f)

# --- Color mapping ---
CALENDAR_COLORS = {
    "Perséinleche Kalenner": "#1f77b4",
    "Gemeinsam CIS Kalenner": "#ff7f0e",
    "PP Kalenner": "#2ca02c",
    "PV Kalenner": "#ff00ff",
    "Batiment": "#9467bd",
    "Gefierer": "#d62728",
    "Instruktiounssaal": "#17becf"
}

def show_event_form(events, user=None):
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True)
    st.subheader("Neien Evenement erstellen")

    calendar_type = st.selectbox(
        "Typ vum Kalenner",
        list(CALENDAR_COLORS.keys())
    )

    vehicle = None
    if calendar_type == "Gefierer":
        vehicle_list = load_vehicles()
        vehicle = st.selectbox(
            "Gefier auswielen",
            vehicle_list if vehicle_list else []
        )

    with st.form("event_form", clear_on_submit=True):
        title = st.text_input("Titel")
        description = st.text_area("Beschreiwung")

        start_date = st.date_input("Ufank Datum")
        end_date = st.date_input("Enn Datum")

        all_day = st.checkbox("Ganzen Daag")

        if not all_day:
            start_time = st.time_input("Ufank Zäit", value=time(0,0))
            end_time = st.time_input("Enn Zäit", value=time(23,59))
        else:
            start_time = time(0, 0)
            end_time = time(23, 59)

        start = datetime.combine(start_date, start_time)
        end = datetime.combine(end_date, end_time)

        submitted = st.form_submit_button("Späicheren")

        if submitted:
            if end < start:
                st.error("❌ Enn Datum/Zäit däerf net virum Ufank sinn!")
            elif not title.strip():
                st.error("❌ Titel däerf net eidel sinn!")
            else:
                new_event = {
                    "title": title,
                    "description": description,
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "calendar_type": calendar_type,
                    "color": CALENDAR_COLORS.get(calendar_type, "#000000"),
                    "all_day": all_day
                }
                if vehicle:
                    new_event["vehicle"] = vehicle

                events.append(new_event)
                save_events(events)
                st.success("✅ Evenement gouf ugeluecht!")

    st.markdown("</div>", unsafe_allow_html=True)

def show_event_list(events, user=None):
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True)
    st.subheader("All Evenementer")
    if events:
        for i, e in enumerate(events):
            start_dt = datetime.fromisoformat(e["start"])
            end_dt = datetime.fromisoformat(e["end"])

            color = e.get("color", "#000000")
            label_html = f"""
                <div style="background-color:{color}; padding:6px; border-radius:4px; display:inline-block; margin-bottom:5px;">
                    {e['calendar_type']}
                </div>
            """
            st.markdown(label_html, unsafe_allow_html=True)

            with st.expander(f"{e['title']}"):
                st.markdown("<strong>Beschreiwung:</strong>", unsafe_allow_html=True)
                st.markdown(e['description'], unsafe_allow_html=True)

                if e.get("all_day", False):
                    st.markdown(f"<p><strong>Datum:</strong> {start_dt.strftime('%d.%m.%Y')} (Ganzen Daag)</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p><strong>Ufank:</strong> {start_dt.strftime('%d.%m.%Y %H:%M')}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><strong>Enn:</strong> {end_dt.strftime('%d.%m.%Y %H:%M')}</p>", unsafe_allow_html=True)
                st.write(f"**Kalender Typ:** {e['calendar_type']}")
                if e.get("vehicle"):
                    st.write(f"**Gefier:** {e['vehicle']}")

                if st.button("🗑️", key=f"delete_{i}"):
                    events.pop(i)
                    save_events(events)
                    st.rerun()

    else:
        st.info("Keng Evenementer fonnt.")

    st.markdown("</div>", unsafe_allow_html=True)

def show_visual_calendar(events):
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True)
    st.subheader("Visuelle Kalenner")

    # The calendar types you want to filter on
    calendar_types = [
        "Perséinleche Kalenner",
        "Gemeinsam CIS Kalenner",
        "PP Kalenner",
        "PV Kalenner",
        "Batiment",
        "Gefierer",
        "Instruktiounssaal"
    ]

    # Multiselect for user to pick which to show (default all selected)
    selected_types = st.multiselect(
        "Wielt Kalenner Typen déi gewisen ginn:",
        options=calendar_types,
        default=calendar_types
    )

    # Filter events based on selected types
    filtered_events = [e for e in events if e.get("calendar_type") in selected_types]

    # Prepare event data for calendar component
    calendar_events = []
    for e in filtered_events:
        vehicle = f" ({e['vehicle']})" if e.get("vehicle") else ""
        calendar_events.append({
            "title": f"{e['title']}{vehicle}",
            "start": e["start"],
            "end": e["end"],
            "color": e.get("color", "#000000")
        })


    calendar_html = f"""
    <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.7/index.global.min.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.7/index.global.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.7/locales/lb.global.min.js"></script>

    <div id="calendar-wrapper">
        <div id='calendar'></div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var calendarEl = document.getElementById('calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {{
                initialView: 'dayGridMonth',
                editable: false,
                selectable: false,
                headerToolbar: {{
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay'
                }},
                locale: 'lb',
                events: {calendar_events}
            }});
            calendar.render();
        }});
    </script>
    <style>
        #calendar-wrapper {{
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            max-width: 100%;
        }}
        #calendar {{
            min-width: 600px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: black;
            background-color: white;
            border-radius: 5px;
            padding: 10px;
        }}
    </style>
    """

    st.components.v1.html(calendar_html, height=600, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

def app(entry_only=False, visual_only=False, user=None):
    events = load_events()
    st.title("Kalenner Verwaltung")

    if user:
        st.sidebar.write(f"Logged in as: {user}")

    if entry_only:
        show_event_form(events, user=user)
        show_event_list(events, user=user)
        return

    if visual_only:
        show_visual_calendar(events)
        return

    # Default: show all
    show_event_form(events, user=user)
    show_event_list(events, user=user)
    show_visual_calendar(events)

if __name__ == "__main__":
    app()

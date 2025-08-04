import streamlit as st
import json
import os
from datetime import datetime
import uuid


JOURNAL_FILE = "tagebuch.json"
CHECKLIST_FILE = "checklist.json"


def load_entries():
    if not os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(JOURNAL_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(JOURNAL_FILE, "w") as f:
            json.dump([], f)
        return []

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

def save_entries(entries):
    with open(JOURNAL_FILE, "w") as f:
        json.dump(entries, f, indent=2)

def save_checklist(items):
    with open(CHECKLIST_FILE, "w") as f:
        json.dump(items, f, indent=2)

def app(user):
    st.title("Tagebuch")

    if not user:
        st.warning("Dir sidd net ageloggt. Bitte loggt Iech an.")
        return

    st.write(f"Verbonnen als **{user}**")

    entries = load_entries()
    checklist_items = load_checklist()

    # Parse datetime strings with correct format
    def parse_datetime(dt_str):
        return datetime.strptime(dt_str, "%d.%m.%Y %H:%M")

    # Get years and months available
    years = sorted({parse_datetime(e["datetime"]).year for e in entries}, reverse=True)
    if not years:
        years = [datetime.now().year]
    selected_year = st.selectbox("Joer wielen", years, index=0)

    months_dict = {
        1: "Januar", 2: "Februar", 3: "Mäerz", 4: "Abrëll",
        5: "Mee", 6: "Juni", 7: "Juli", 8: "August",
        9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
    }
    selected_month = st.selectbox("Mount wielen", list(months_dict.values()), index=datetime.now().month - 1)
    selected_month_num = [k for k, v in months_dict.items() if v == selected_month][0]

    search_text = st.text_input("Sichen (CTRL+F)")

    # Filter entries by year, month, and search text
    filtered_entries = [
        e for e in entries
        if parse_datetime(e["datetime"]).year == selected_year
        and parse_datetime(e["datetime"]).month == selected_month_num
    ]

    if search_text.strip():
        filtered_entries = [
            e for e in filtered_entries
            if search_text.lower() in e["user"].lower() or search_text.lower() in e["content"].lower()
        ]

    if filtered_entries:
        for i, e in enumerate(filtered_entries):
            dt = parse_datetime(e["datetime"])
            st.markdown(f"**{e['user']}** - {dt.strftime('%d.%m.%Y %H:%M')}")
            st.write(e["content"])

            if e["user"] == user:
                if st.button("🗑️", key=f"del_{e['datetime']}_{i}"):
                    # Remove from entries list all except this one
                    entries = [entry for entry in entries if not (
                        entry["datetime"] == e["datetime"] and
                        entry["user"] == e["user"] and
                        entry["content"] == e["content"]
                    )]
                    save_entries(entries)
                    st.rerun()

            st.markdown("---")
    else:
        st.info("Keng Entrée fonnt fir dësen Mount / Joer.")


    # --- New Entry Form with checklist option ---
    st.markdown("### Nei Entrée derbäisetzen")
    with st.form("new_entry_form", clear_on_submit=True):
        content = st.text_area("Ären Text")
        is_checklist = st.checkbox("Als To-Do derbäisetzen", value=False)
        submitted = st.form_submit_button("Späicheren")

        if submitted:
            if not content.strip():
                st.error("De Text däerf net eidel sinn!")
            else:
                if is_checklist:
                    # Load existing checklist (simple list of dicts with id and text only)
                    checklist = load_checklist()
                    new_item = {
                        "id": str(uuid.uuid4()),
                        "text": content,
                    }
                    checklist.append(new_item)
                    save_checklist(checklist)
                    st.success("To-Do erfollegräich derbäigesat!")
                else:
                    new_entry = {
                        "user": user,
                        "content": content,
                        "datetime": datetime.now().strftime("%d.%m.%Y %H:%M")
                    }
                    entries.append(new_entry)
                    save_entries(entries)
                    st.success("Entrée erfollegräich derbäigesat!")

# --- Display the checklist with delete buttons (no checkboxes) ---
    st.markdown("### To do")

    checklist_items = load_checklist()

    if checklist_items:
        for item in checklist_items:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
            # Just show text as a bullet point (no checkbox)
                st.markdown(f"- {item['text']}")
            with col2:
                if st.button("🗑️", key=f"delete_{item['id']}"):
                    checklist_items = [i for i in checklist_items if i["id"] != item["id"]]
                    save_checklist(checklist_items)
                    st.rerun()
    else:
        st.info("Keng Checkliste verfügbar.")


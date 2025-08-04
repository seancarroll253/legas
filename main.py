import streamlit as st

st.set_page_config(
    layout="centered",
    page_title="Legasi v1.0",
    page_icon="🚒"
)

# 🔐 Allowed users
ALLOWED_USERS = {
    "Sean": "123456"
}

# ✅ Initialize session state keys
if "username" not in st.session_state:
    st.session_state.username = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

import calendar_page
import dashboard
import tagebuch_page
import water_level

# 🔐 Login function
def login():

    # Logo + CIS Mersch + Program centered above login form
    st.markdown(
        """
        <div style="text-align: center; padding-bottom: 20px;">
            <img src="https://i.postimg.cc/5t3RGkb0/1200px-CGDIS-icon-of-logo-svg.png" style="height: 120px;"><br>
            <p style="font-size: 30px; color: black; margin: 0;">Legasi v1.0</p>
        </div>
        """,
        unsafe_allow_html=True
    )


    st.title("Login")
    username = st.text_input("Benotzernumm").strip()
    password = st.text_input("Passwuert", type="password").strip()

    # Initialize a session state key for button press
    if "login_pressed" not in st.session_state:
        st.session_state.login_pressed = False

    if st.button("Login") or st.session_state.login_pressed:
        st.session_state.login_pressed = True  # remember that login was pressed

        if username.lower() == "sean" and password == "123456":
            st.session_state.username = username
            st.session_state.logged_in = True
            st.success("Erfollegräich ageloggt!")
            st.session_state.login_pressed = False  # reset after successful login
            st.rerun()
        else:
            st.error("Falschen Benotzernumm oder Passwuert!")
            st.session_state.login_pressed = False  # reset on fail


# 🚪 Logout function
def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# 🔐 Login Gate
if not st.session_state.logged_in:
    login()
else:
    # 🎉 Authenticated area
    # --- Global CSS styles ---
    
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

    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """, unsafe_allow_html=True)


    # 🧭 Sidebar
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; padding-bottom: 10px;">
            <img src="https://i.postimg.cc/5t3RGkb0/1200px-CGDIS-icon-of-logo-svg.png" style="height: 40px; margin-right: 10px;">
            <h2 style="margin: 0; color: black;">CIS Mersch</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.title(f"Salut {st.session_state.username}")
    logout()

    # 🧭 Navigation
    st.sidebar.title("Navigatioun")
    page = st.sidebar.selectbox("Säit auswielen", ["Dashboard", "Kalenner Entrée", "Visuelle Kalenner", "Tagebuch", "Waasserstänn"])


    if page == "Dashboard":
        dashboard.app()

    elif page == "Waasserstänn":
        water_level.app()

    elif page == "Kalenner Entrée":
        calendar_page.app(entry_only=True)

    elif page == "Visuelle Kalenner":
        calendar_page.app(visual_only=True)

    elif page == "Tagebuch":
        tagebuch_page.app(user=st.session_state.username)




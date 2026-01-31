import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pydeck as pdk

# ==================================================
# Page Configuration
# ==================================================
st.set_page_config(
    page_title="Researcher Profile | Climate & STEM Explorer",
    page_icon="🌍",
    layout="wide"
)

# ==================================================
# API KEY (from Streamlit Secrets)
# ==================================================
API_KEY = st.secrets["OPENWEATHER_API_KEY"]

# ==================================================
# City Configuration (South Africa)
# ==================================================
CITIES = {
    "Pretoria": {"lat": -25.7479, "lon": 28.2293},
    "Johannesburg": {"lat": -26.2041, "lon": 28.0473},
    "Cape Town": {"lat": -33.9249, "lon": 18.4241},
    "Durban": {"lat": -29.8587, "lon": 31.0218},
    "Polokwane": {"lat": -23.8962, "lon": 29.4486}
}

# ==================================================
# Dark / Light Mode Toggle
# ==================================================
st.sidebar.title("⚙️ Settings")
theme_mode = st.sidebar.radio("Theme", ["Light Mode", "Dark Mode"])

if theme_mode == "Dark Mode":
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    h1, h2, h3 {
        color: #4fa3ff;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
    .stMetric {
        background-color: #1f2933;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #1f3c88;
    }
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    .stMetric {
        background-color: #f5f7fa;
    }
    </style>
    """, unsafe_allow_html=True)

# ==================================================
# Helper Functions
# ==================================================
def load_cv():
    with open("Munei_Mugeri_CV.pdf", "rb") as f:
        return f.read()

def get_current_weather(city):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    r = requests.get(url)
    if r.status_code == 200:
        d = r.json()
        return {
            "City": city,
            "Temperature (°C)": d["main"]["temp"],
            "Humidity (%)": d["main"]["humidity"],
            "Condition": d["weather"][0]["description"].title(),
            "Wind (m/s)": d["wind"]["speed"],
            "Latitude": d["coord"]["lat"],
            "Longitude": d["coord"]["lon"]
        }
    return None

def get_forecast(city):
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        records = []
        for item in data["list"]:
            records.append({
                "Datetime": datetime.fromtimestamp(item["dt"]),
                "Temperature (°C)": item["main"]["temp"],
                "Humidity (%)": item["main"]["humidity"]
            })
        return pd.DataFrame(records)
    return None

# ==================================================
# Sidebar Navigation
# ==================================================
st.sidebar.title("🧭 Navigation")
menu = st.sidebar.radio(
    "Go to:",
    ["Researcher Profile", "Publications", "STEM Data Explorer", "Contact"]
)

# ==================================================
# Researcher Profile
# ==================================================
if menu == "Researcher Profile":
    st.title("👨‍🔬 Researcher Profile")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(
            "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
            use_container_width=True
        )

    with col2:
        st.subheader("Mr. Munei Mugeri")
        st.markdown("**Meteorologist | Climate & Atmospheric Scientist**")

        st.markdown("""
        I am a meteorology researcher specializing in **climate variability,
        weather extremes, and atmospheric data analysis**, with a focus on
        Southern African climate systems.
        """)

        st.markdown("""
        **🏛️ Institution:** University of Pretoria  
        **📍 Focus Area:** Climate analysis & weather modeling  
        **🔬 Interests:** Climate change, extremes, environmental data science  
        """)

        st.markdown("🔗 **LinkedIn:** https://www.linkedin.com")

    st.divider()

    st.subheader("📄 Curriculum Vitae")
    st.download_button(
        "⬇️ Download CV (PDF)",
        data=load_cv(),
        file_name="Munei_Mugeri_CV.pdf",
        mime="application/pdf"
    )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Years Experience", "5+")
    c2.metric("Projects", "12")
    c3.metric("Datasets", "30+")
    c4.metric("Publications", "8")

# ==================================================
# Publications
# ==================================================
elif menu == "Publications":
    st.title("📚 Publications")

    uploaded = st.file_uploader("Upload Publications CSV", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df, use_container_width=True)

        keyword = st.text_input("🔎 Filter by keyword")
        if keyword:
            df = df[df.apply(
                lambda r: keyword.lower() in r.astype(str).str.lower().values,
                axis=1
            )]
            st.dataframe(df, use_container_width=True)

        if "Year" in df.columns:
            st.subheader("📈 Publication Trends")
            st.line_chart(df["Year"].value_counts().sort_index())

# ==================================================
# STEM Data Explorer (Weather, Forecast, Maps)
# ==================================================
elif menu == "STEM Data Explorer":
    st.title("🌦️ Climate & Weather Explorer")

    selected_cities = st.multiselect(
        "Select cities",
        list(CITIES.keys()),
        default=["Pretoria"]
    )

    if selected_cities:
        st.subheader("📊 Current Weather Conditions")

        weather_data = []
        for city in selected_cities:
            data = get_current_weather(city)
            if data:
                weather_data.append(data)

        weather_df = pd.DataFrame(weather_data)
        st.dataframe(
            weather_df.drop(columns=["Latitude", "Longitude"]),
            use_container_width=True
        )

        st.bar_chart(weather_df.set_index("City")["Temperature (°C)"])

        # ---------------- WEATHER MAP ----------------
        st.subheader("🗺️ Weather Map (Temperature Intensity)")

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=weather_df,
            get_position='[Longitude, Latitude]',
            get_radius=45000,
            get_fill_color='[255, 140 - Temperature * 4, 0]',
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=weather_df["Latitude"].mean(),
            longitude=weather_df["Longitude"].mean(),
            zoom=5
        )

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{City}\nTemp: {Temperature (°C)} °C"}
        ))

        # ---------------- FORECAST ----------------
        st.divider()
        st.subheader("⏱️ 5-Day Time-Series Forecast")

        city_forecast = st.selectbox(
            "Select city for forecast",
            selected_cities
        )

        forecast_df = get_forecast(city_forecast)
        if forecast_df is not None:
            forecast_df = forecast_df.set_index("Datetime")
            st.line_chart(
                forecast_df[["Temperature (°C)", "Humidity (%)"]]
            )

# ==================================================
# Contact
# ==================================================
elif menu == "Contact":
    st.title("📬 Contact")

    st.markdown("""
    **Open to collaborations, research partnerships, and climate-related projects.**
    """)

    st.info("📧 Email: muneidrummer@gmail.com")
    st.success("🔗 LinkedIn: https://www.linkedin.com")

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pydeck as pdk
from PIL import Image
import os

# ==================================================
# Page Configuration
# ==================================================
st.set_page_config(
    page_title="Researcher Profile | Climate & STEM Explorer",
    page_icon="🌍",
    layout="wide"
)

# ==================================================
# Dark Academic Theme (GLOBAL)
# ==================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0e1117;
    color: #e6e6e6;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 {
    color: #4fa3ff;
}
[data-testid="stSidebar"] {
    background-color: #161b22;
}
.stMetric {
    background-color: #1f2933;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

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
    ["Researcher Profile", "Publications", "Weather and Climate data explorer", "Contact"]
)

# ==================================================
# Researcher Profile
# ==================================================
if menu == "Researcher Profile":
    st.title("👨‍🔬 Researcher Profile")

    # --- Top section: Thunderstorm image + Profile info ---
    col1, col2 = st.columns([1, 2])

    with col1:
        storm_image_path = os.path.join(
            os.path.dirname(__file__),
            "thunderstorms.jpg"
        )

        storm_img = Image.open(storm_image_path)

        st.image(
            storm_img,
            caption="Thunderstorm & Atmospheric Dynamics",
            use_container_width=True
        )


    with col2:
        # Name + personal photo side-by-side
        name_col, photo_col = st.columns([3, 1])

        with name_col:
            st.subheader("Mr. Munei Mugeri")
            st.markdown("**Meteorologist | Remote Sensing Scientist**")

        with photo_col:
            image_path = os.path.join(os.path.dirname(__file__), "myself.jpg")

            profile_img = Image.open(image_path)

            st.image(
                profile_img,
                use_container_width=True
            )

        st.markdown("""
        I am a meteorology researcher specializing in radars, satellites and lightning detection networks with a strong focus
        on Southern African climate systems.
        """)

        st.markdown("""
        **🏛️ Institution:** South African Weather Service  
        **📍 Focus Area:** Remote Sensing Research  
        **🔬 Research Interests:** Radar algorithms, nowcasting, Hail estimates 
        """)

        st.markdown("🔗 **LinkedIn:** https://www.linkedin.com/in/munei-mugeri-09502b14b/")

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
# STEM Data Explorer (Weather, Maps, Forecast)
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

        st.divider()
        st.subheader("5-Day Time-Series Forecast")

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
    st.title("Contact")

    st.markdown("""
    **Open to collaborations, research partnerships, and climate-related projects.**
    """)

    st.info("📧 Email: muneidrummer@gmail.com")
    st.success("🔗 LinkedIn: https://www.linkedin.com/in/munei-mugeri-09502b14b/")





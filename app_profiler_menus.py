import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pydeck as pdk
from PIL import Image
import os
import base64

# Set page title
st.set_page_config(
    page_title="Researcher Profile | Climate & STEM Explorer",
    page_icon="🌍",
    layout="wide"
)

# Set background theme
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #ffffff;
    color: #1b1b1b;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 {
    color: #1f77b4;
}
[data-testid="stSidebar"] {
    background-color: #f0f2f6;
}
.stMetric {
    background-color: #e6e6e6;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Set helper functions
def load_cv():
    path = os.path.join(os.path.dirname(__file__), "Munei_Mugeri_CV.pdf")
    with open(path, "rb") as f:
        return f.read()

def get_current_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
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
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        records = []
        for item in data["list"]:
            records.append({
                "Datetime": datetime.fromtimestamp(item["dt"]),
                "Temperature (°C)": item["main"]["temp"],
                "Humidity (%)": item["main"]["humidity"],
                "Rain (mm)": item.get("rain", {}).get("3h", 0),
                "Precip Prob (%)": item.get("pop", 0) * 100
            })
        return pd.DataFrame(records)
    return None

# Set API Key and Cities
API_KEY = st.secrets.get("OPENWEATHER_API_KEY")
if API_KEY is None:
    st.error("OpenWeather API key not found in Streamlit secrets.")
    st.stop()

CITIES = {
    "Pretoria": {"lat": -25.7479, "lon": 28.2293},
    "Johannesburg": {"lat": -26.2041, "lon": 28.0473},
    "Cape Town": {"lat": -33.9249, "lon": 18.4241},
    "Durban": {"lat": -29.8587, "lon": 31.0218},
    "Polokwane": {"lat": -23.8962, "lon": 29.4486}
}

# Sidebar Menu
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to:",
    ["Researcher Profile", "Publications", "Weather and Climate Data Explorer", "Contact"]
)

# Sections based on menu selection
if menu == "Researcher Profile":
    st.title("Researcher Profile")

    col1, col2 = st.columns([1, 2])

    with col1:
        storm_image_path = os.path.join(os.path.dirname(__file__), "thunderstorms.jpg")
        if os.path.exists(storm_image_path):
            storm_img = Image.open(storm_image_path)
            # Resize the image to be more portrait (taller)
            width, height = storm_img.size
            new_height = int(width * 1.5)  # make height 1.5x width for portrait effect
            storm_img = storm_img.resize((width, new_height))
            st.image(storm_img, use_container_width=True)
        else:
            st.warning("Storm image not found.")


    with col2:
        name_col, photo_col = st.columns([3, 1])
        with name_col:
            st.subheader("Mr. Munei Mugeri")
            st.markdown("**Meteorologist | Weather and Climate variability Scientist**")
        with photo_col:
            image_path = os.path.join(os.path.dirname(__file__), "myself.jpg")
            if os.path.exists(image_path):
                profile_img = Image.open(image_path)
                st.image(profile_img, use_container_width=True)
            else:
                st.warning("Profile image not found.")

        st.markdown("""
        I am a meteorology researcher specializing in Extreme weather events, climate variability
        and lightning detection networks, with a strong focus on Southern African climate systems.
        """)
        st.markdown("""
        **🏛️ Institution:** South African Weather Service  
        **📍 Focus Area:** Weather and climate variability Research  
        **🔬 Research Interests:** Extreme weather events, nowcasting, Temperature anomalies 
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
    c1.metric("Years Experience", "3+")
    c2.metric("Projects", "6")
    c3.metric("Datasets", "30+")
    c4.metric("Publications", "5")

elif menu == "Publications":
    st.title("📚 Publications")

    # Upload publications file
    uploaded = st.file_uploader("Upload Publications CSV", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df, use_container_width=True)
        
        # Add filtering for year or keyword
        keyword = st.text_input("Filter by keyword")
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
# Weather & Climate Data Explorer (NO MAP)
# ==================================================
elif menu == "Weather and Climate Data Explorer":
    st.title("🌦️ Weather & Climate Explorer")

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

        st.subheader("🌡️ Temperature Comparison")
        st.bar_chart(
            weather_df.set_index("City")["Temperature (°C)"]
        )

        st.divider()

        st.subheader("📈 5-Day Forecast (Temperature, Humidity & Precipitation)")

        city_forecast = st.selectbox(
            "Select city for forecast",
            selected_cities
        )

        forecast_df = get_forecast(city_forecast)

        if forecast_df is not None:
            forecast_df = forecast_df.set_index("Datetime")

            st.line_chart(
                forecast_df[
                    ["Temperature (°C)", "Humidity (%)", "Rain (mm)", "Precip Prob (%)"]
                ]
            )


# Add a contact section
elif menu == "Contact":
    st.title("Contact")
    st.markdown("**For collaborations, research partnerships, and climate-related projects, you can reach me at:**")
    st.info("📧 Email: muneidrummer@gmail.com")
    st.success("🔗 LinkedIn: https://www.linkedin.com/in/munei-mugeri-09502b14b/")







import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# ==================================================
# Page Config
# ==================================================
st.set_page_config(
    page_title="Researcher Profile | STEM & Climate Explorer",
    page_icon="🌍",
    layout="wide"
)

# ==================================================
# Custom Academic Theme (CSS)
# ==================================================
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 {
    color: #1f3c88;
}
.stMetric {
    background-color: #f5f7fa;
    padding: 15px;
    border-radius: 10px;
}
[data-testid="stSidebar"] {
    background-color: #f0f2f6;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# Helper Functions
# ==================================================
def load_cv():
    with open("Munei_Mugeri_CV.pdf", "rb") as file:
        return file.read()

def get_current_weather(city, api_key):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "City": city,
            "Temperature (°C)": data["main"]["temp"],
            "Humidity (%)": data["main"]["humidity"],
            "Condition": data["weather"][0]["description"].title(),
            "Wind (m/s)": data["wind"]["speed"]
        }
    return None

def get_weather_forecast(city, api_key):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={api_key}&units=metric"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
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
            use_column_width=True
        )

    with col2:
        st.subheader("Mr. Munei Mugeri")
        st.markdown("**Meteorologist | Climate & Atmospheric Scientist**")

        st.markdown("""
        I am a meteorology researcher with interests in **climate variability, weather extremes,
        and data-driven atmospheric analysis**. My work focuses on applying scientific methods
        and modern data tools to real-world environmental challenges.
        """)

        st.markdown("""
        **🏛️ Institution:** University of Pretoria  
        **📍 Current Focus:** Climate data analysis & weather modeling  
        **🔬 Research Interests:**  
        - Climate Change & Variability  
        - Extreme Weather Events  
        - Environmental Data Science  
        """)

        st.markdown(
            "🔗 **LinkedIn:** [linkedin.com/in/munei-mugeri](https://www.linkedin.com)"
        )

    st.divider()

    st.subheader("📄 Curriculum Vitae")
    st.download_button(
        "⬇️ Download CV (PDF)",
        data=load_cv(),
        file_name="Munei_Mugeri_CV.pdf",
        mime="application/pdf"
    )

    st.divider()

    st.subheader("📊 Research Snapshot")
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

    uploaded_file = st.file_uploader("Upload Publications CSV", type="csv")

    if uploaded_file:
        publications = pd.read_csv(uploaded_file)
        st.dataframe(publications, use_container_width=True)

        keyword = st.text_input("🔎 Filter by keyword")
        if keyword:
            publications = publications[
                publications.apply(
                    lambda row: keyword.lower() in row.astype(str).str.lower().values,
                    axis=1
                )
            ]
            st.dataframe(publications, use_container_width=True)

        if "Year" in publications.columns:
            st.subheader("📈 Publication Trends")
            st.line_chart(publications["Year"].value_counts().sort_index())

# ==================================================
# STEM Data Explorer
# ==================================================
elif menu == "STEM Data Explorer":
    st.title("🧪 STEM Data Explorer")

    api_key = st.secrets["OPENWEATHER_API_KEY"]

    cities = st.multiselect(
        "Select cities",
        ["Cape Town", "London", "New York", "Tokyo", "Sydney"],
        default=["Cape Town"]
    )

    if cities:
        st.subheader("🌦️ Current Weather Conditions")
        weather_data = []

        for city in cities:
            data = get_current_weather(city, api_key)
            if data:
                weather_data.append(data)

        weather_df = pd.DataFrame(weather_data)
        st.dataframe(weather_df, use_container_width=True)
        st.bar_chart(weather_df.set_index("City")["Temperature (°C)"])

        st.divider()

        st.subheader("⏱️ 5-Day Weather Forecast (Time Series)")
        forecast_city = st.selectbox("Choose city for forecast", cities)

        forecast_df = get_weather_forecast(forecast_city, api_key)
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
    **Interested in collaboration or research discussions?**  
    Feel free to reach out.
    """)

    st.info("📧 Email: muneidrummer@gmail.com")
    st.success("🔗 LinkedIn: https://www.linkedin.com")

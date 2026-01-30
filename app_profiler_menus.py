import streamlit as st
import pandas as pd
import numpy as np

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Researcher Profile | STEM Data Explorer", page_icon="🌍", layout="wide")

# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Go to:",
    ["Researcher Profile", "Publications", "STEM Data Explorer", "Contact"],
)

# --------------------------------------------------
# Dummy STEM Data
# --------------------------------------------------
physics_data = pd.DataFrame({
    "Experiment": ["Alpha Decay", "Beta Decay", "Gamma Ray Analysis", "Quark Study", "Higgs Boson"],
    "Energy (MeV)": [4.2, 1.5, 2.9, 3.4, 7.1],
    "Date": pd.date_range(start="2024-01-01", periods=5),
})

astronomy_data = pd.DataFrame({
    "Celestial Object": ["Mars", "Venus", "Jupiter", "Saturn", "Moon"],
    "Brightness (Magnitude)": [-2.0, -4.6, -1.8, 0.2, -12.7],
    "Observation Date": pd.date_range(start="2024-01-01", periods=5),
})

weather_data = pd.DataFrame({
    "City": ["Cape Town", "London", "New York", "Tokyo", "Sydney"],
    "Temperature (°C)": [25, 10, -3, 15, 30],
    "Humidity (%)": [65, 70, 55, 80, 50],
    "Recorded Date": pd.date_range(start="2024-01-01", periods=5),
})

# ==================================================
# Researcher Profile
# ==================================================
if menu == "Researcher Profile":
    st.title("Researcher Profile")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(
            "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
            caption="Climate & Atmosphere Research",
            use_column_width=True
        )

    with col2:
        st.subheader("Mr. Munei Mugeri")
        st.markdown("**Meteorologist | Climate & Atmospheric Researcher**")

        st.markdown("""
         **Short Bio**  
        I am a highly motivated, enthusiastic, versatile, and hardworking researcher
        with a strong academic background in meteorologu and experience in air quality
        management. I am a dedicated, innovative person who values collective thought
        in solving problems and pursuit for excellence.
        """)

        st.markdown("""
         **Institution:** University of Pretoria  
         **Currently Working On:** Remote Sensing Research  
         **Research Interests:**  
        - Hail estimates  
        - Radar algorithms  
        - Moisture sources & transport  
        """)

        st.markdown(
            " **LinkedIn:** "
            "[linkedin.com/in/munei-mugeri](https://www.linkedin.com)"
        )

    st.divider()

    # Key Metrics
    st.subheader("Research Snapshot")
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Years of Research", "5+")
    m2.metric("Projects Completed", "12")
    m3.metric("Datasets Analyzed", "30+")
    m4.metric("Publications", "8")

    st.divider()

    # Simple Visualization
    st.subheader("Research Focus Areas")
    focus_data = pd.DataFrame({
        "Area": ["Climate Analysis", "Weather Forecasting", "Data Science", "Environmental Studies"],
        "Focus Level": [35, 25, 20, 20]
    })

    st.bar_chart(
        focus_data.set_index("Area")
    )

# ==================================================
# Publications
# ==================================================
elif menu == "Publications":
    st.title("Publications")
    st.sidebar.header("Upload and Filter")

    uploaded_file = st.file_uploader("Upload a CSV of Publications", type="csv")

    if uploaded_file:
        publications = pd.read_csv(uploaded_file)
        st.dataframe(publications, use_container_width=True)

        keyword = st.text_input("Filter by keyword")
        if keyword:
            filtered = publications[
                publications.apply(
                    lambda row: keyword.lower() in row.astype(str).str.lower().values,
                    axis=1
                )
            ]
            st.write(f"### Results for '{keyword}'")
            st.dataframe(filtered, use_container_width=True)

        if "Year" in publications.columns:
            st.subheader("Publication Trends")
            year_counts = publications["Year"].value_counts().sort_index()
            st.line_chart(year_counts)

# ==================================================
# STEM Data Explorer
# ==================================================
elif menu == "STEM Data Explorer":
    st.title("STEM Data Explorer")
    st.sidebar.header("Data Selection")

    data_option = st.sidebar.selectbox(
        "Choose a dataset",
        ["Physics Experiments", "Astronomy Observations", "Weather Data"]
    )

    if data_option == "Physics Experiments":
        st.subheader("Physics Experiments")
        st.dataframe(physics_data, use_container_width=True)

        energy_filter = st.slider("Energy (MeV)", 0.0, 10.0, (0.0, 10.0))
        filtered = physics_data[
            physics_data["Energy (MeV)"].between(*energy_filter)
        ]
        st.bar_chart(filtered.set_index("Experiment")["Energy (MeV)"])

    elif data_option == "Astronomy Observations":
        st.subheader("Astronomy Observations")
        st.dataframe(astronomy_data, use_container_width=True)

        brightness_filter = st.slider("Brightness (Magnitude)", -15.0, 5.0, (-15.0, 5.0))
        filtered = astronomy_data[
            astronomy_data["Brightness (Magnitude)"].between(*brightness_filter)
        ]
        st.line_chart(filtered.set_index("Celestial Object")["Brightness (Magnitude)"])

    elif data_option == "Weather Data":
        st.subheader("Weather Data")
        st.dataframe(weather_data, use_container_width=True)

        temp_filter = st.slider("Temperature (°C)", -10.0, 40.0, (-10.0, 40.0))
        humidity_filter = st.slider("Humidity (%)", 0, 100, (0, 100))

        filtered = weather_data[
            weather_data["Temperature (°C)"].between(*temp_filter) &
            weather_data["Humidity (%)"].between(*humidity_filter)
        ]

        st.area_chart(filtered.set_index("City")[["Temperature (°C)", "Humidity (%)"]])

# ==================================================
# Contact
# ==================================================
elif menu == "Contact":
    st.title("Contact")

    st.markdown("""
    **Let’s connect!**  
    Feel free to reach out for collaboration, research discussions, or projects.
    """)

    st.info("Email: muneidrummer@gmail.com")
    st.success("LinkedIn: https://www.linkedin.com/in/munei-mugeri-09502b14b/")


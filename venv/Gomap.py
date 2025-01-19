import streamlit as st
from sqlalchemy.orm import Session
from models import TrainStationGL, Travel  # Import Travel model
from database import get_db, get_banlieue_tunis_stations, get_banlieue_sahel_stations, get_station_options
import requests

# API URL (replace with your actual API endpoint)
API_URL = "http://127.0.0.1:8000"  # Replace with your API URL

# Initialize session state for login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Display an image at the top of the page (optional)
st.image("SNCFT.png", caption="Welcome to SNCFT", use_container_width=True)

# Title for the main page
st.title("Main Page")

# Hide Streamlit's default radio button style
st.markdown("""
    <style>
    .stRadio > div { 
        flex-direction: row;
        justify-content: space-around;
    }
    .stRadio label {
        font-size: 18px;
        font-weight: bold;
        color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# Function to transform station name to standard format
def transform_station_name(station_name):
    return f"{station_name.strip().lower()} train station".title()

# Main Page Logic
if not st.session_state.logged_in:
    page_selection = st.radio("Choose an option", ("Sign Up", "Log In"))

    if page_selection == "Sign Up":
        st.header("Create Your Account")
        name = st.text_input("Name", placeholder="Enter your name")
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", placeholder="Enter your password", type="password")
        confirm_password = st.text_input("Confirm Password", placeholder="Re-enter your password", type="password")
        if st.button("Sign Up"):
            if not name or not email or not password or not confirm_password:
                st.error("All fields are required.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                payload = {"Name": name, "Email": email, "Password": password}
                response = requests.post(f"{API_URL}/signup", json=payload)
                if response.status_code == 200:
                    st.success(f"Account created successfully for {name}!")
                    st.info("You can now log in.")
                else:
                    st.error(f"Error: {response.text}")
    elif page_selection == "Log In":
        st.header("Log In to Your Account")
        email = st.text_input("Email", placeholder="Email")
        password = st.text_input("Password", placeholder="Enter your password", type="password")
        if st.button("Log In"):
            if not email or not password:
                st.error("Both email and password are required.")
            else:
                payload = {"username": email, "password": password}
                response = requests.post(f"{API_URL}/login", data=payload)
                if response.status_code == 200:
                    user_data = response.json()
                    st.session_state.logged_in = True
                    st.session_state.user_name = user_data.get("name", "User")
                    st.success(f"{user_data['message']}!")
                else:
                    st.error("Invalid username or password. Please try again.")
else:
    st.header(f"Welcome, {st.session_state.user_name}!")
    line_options = ["Grandes Lignes", "Banlieue de Tunis", "Banlieue du Sahel"]
    with next(get_db()) as db:
        stations_grandes_lignes = [station[0] for station in get_station_options(db)]
        stations_banlieue_tunis = [station[0] for station in get_banlieue_tunis_stations(db)]
        stations_banlieue_sahel = [station[0] for station in get_banlieue_sahel_stations(db)]

    selected_line = st.radio("Choisissez la ligne :", line_options, horizontal=True)

    if selected_line == "Grandes Lignes":
        departure_stations = stations_grandes_lignes
        arrival_stations = stations_grandes_lignes
    elif selected_line == "Banlieue de Tunis":
        departure_stations = stations_banlieue_tunis
        arrival_stations = stations_banlieue_tunis
    elif selected_line == "Banlieue du Sahel":
        departure_stations = stations_banlieue_sahel
        arrival_stations = stations_banlieue_sahel

    if 'departure_stations' in locals():
        departure_station = st.selectbox("Gare de Départ :", departure_stations)
        arrival_station = st.selectbox("Gare d'Arrivée :", arrival_stations)

        # Apply transformation
        transformed_departure_station = transform_station_name(departure_station)
        transformed_arrival_station = transform_station_name(arrival_station)

        if departure_station == arrival_station:
            st.warning("La gare de départ et d'arrivée ne peuvent pas être identiques.")
        else:
            departure_date = st.date_input("Date de départ :")

            # Define columns without nesting
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Button layout
                button_col1, button_col2 = st.columns(2)

                # "Check Live Location" button
                with button_col1:
                    if st.button("Check Live Location"):
                        formatted_date = departure_date.strftime('%Y-%m-%d')

                        params = {
                            "origin": transformed_departure_station,
                            "destination": transformed_arrival_station,
                            "travel_date": formatted_date
                        }

                        response = requests.get(f"{API_URL}/get-directions/", params=params)

                        if response.status_code == 200:
                            directions_data = response.json()

                            if directions_data.get("status") == "success":
                                st.subheader("Train Location and Details:")

                                st.markdown(f"### Train: Going from **{transformed_departure_station}** to **{transformed_arrival_station}**")
                                st.markdown(f"**Date of Travel:** {formatted_date}")

                                current_loc = directions_data.get("current_loc", "Location information not available")
                                st.markdown(f"**Current Location:** {current_loc}")

                                col1, col2 = st.columns([1, 1])  # Only one level of columns here
                                with col1:
                                    st.markdown(f"**Estimated Duration:** {directions_data.get('duration', 'Not available')}")
                                with col2:
                                    st.markdown(f"**Estimated Distance:** {directions_data.get('distance', 'Not available')}")
                            else:
                                st.warning(f"**No route found:** {directions_data['status']}")

                        else:
                            st.error(f"**Error fetching directions:** {response.text}")

                # "Check Prices" button
                with button_col2:
                    if st.button("Check Prices"):
                        passenger_type = st.selectbox("Select Passenger Type:", ["old", "student", "child"])

                        formatted_date = departure_date.strftime('%Y-%m-%d')

                        params = {
                            "origin": transformed_departure_station,
                            "destination": transformed_arrival_station,
                            "passenger_type": passenger_type,
                            "date": formatted_date
                        }

                        response = requests.get(f"{API_URL}/check-price/", params=params)

                        if response.status_code == 200:
                            price_data = response.json()
                            st.write("### Price Details:")
                            st.write(f"**Base Price:** {price_data['base_price']} TND")
                            st.write(f"**Final Price:** {price_data['final_price']} TND")
                            st.write(f"**Passenger Type:** {price_data['passenger_type']}")
                        else:
                            st.error(f"Error fetching price: {response.text}")

    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.info("You have been logged out.")


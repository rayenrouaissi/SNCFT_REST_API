import streamlit as st
from sqlalchemy.orm import Session
from models import TrainStationGL, Travel, User 
from database import get_db, get_banlieue_tunis_stations, get_banlieue_sahel_stations, get_station_options
import requests
from datetime import datetime
import time
import urllib.parse
import sendgrid
from sendgrid.helpers.mail import Mail
import random  


API_URL = "http://127.0.0.1:8000"  
BASE_SUCCESS_URL = "http://localhost:8501/"  
SUCCESS_URL = f"{BASE_SUCCESS_URL}?payment_id={{CHECKOUT_SESSION_ID}}"  
SENDGRID_API_KEY = "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" 


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "show_payment_page" not in st.session_state:
    st.session_state.show_payment_page = False
if "price_data" not in st.session_state:
    st.session_state.price_data = None
if "selected_travel" not in st.session_state:
    st.session_state.selected_travel = None
if "payment_url" not in st.session_state:
    st.session_state.payment_url = None
if "show_success_message" not in st.session_state:
    st.session_state.show_success_message = False
if "payment_id" not in st.session_state:
    st.session_state.payment_id = None
if "email" not in st.session_state:
        st.session_state.email = None

if "final_price" not in st.session_state:
        st.session_state.final_price = None
if "show_thank_you_page" not in st.session_state:
    st.session_state.show_thank_you_page = False


st.image("SNCFT.png", caption="Welcome to SNCFT", use_container_width=True)

st.title("SNCFT Dashboard")

def transform_station_name(station_name):
    return f"{station_name.strip().lower()} train station".title()

st.sidebar.title("Navigation & Info")
if st.session_state.logged_in:
    st.sidebar.write(f"Welcome, {st.session_state.user_name}!")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.session_state.show_payment_page = False
        st.session_state.price_data = None
        st.session_state.selected_travel = None
        st.session_state.show_thank_you_page = False
        st.info("You have been logged out.")
else:
    page_selection = st.sidebar.radio("Choose an option", ("Sign Up", "Log In"))

st.sidebar.markdown("---")
st.sidebar.header("Current Date & Time")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.sidebar.write(f"⏰ **Time:** {current_time}")

st.sidebar.markdown("---")
st.sidebar.header("Quick Stats")
st.sidebar.write("🚄 **Total Trains Today:** 42")
st.sidebar.write("⚠️ **Latest Trains Delayed:**")
st.sidebar.write("- Tunis - Sfax")
st.sidebar.write("- Tunis - Gabès")
st.sidebar.write("- Sousse - Monastir")

st.sidebar.markdown("---")
st.sidebar.header("Support")
st.sidebar.write("📞 **Contact Us:** +216 55 246 649")
st.sidebar.write("📧 **Email:** rayenrouaissi7@gmail.com")

if not st.session_state.logged_in:
    if 'page_selection' not in locals():
        page_selection = "Sign Up"  

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
                    with next(get_db()) as db:
                        user = db.query(User).filter(User.Email == email).first()
                        if user:
                            st.session_state.user_name = user.Name
                        else:
                             st.session_state.user_name = "User" 
                    st.session_state.logged_in = True
                    st.session_state.user_email = email  
                    st.success(f"Welcome back {st.session_state.user_name}!")

                else:
                    st.error("Invalid username or password. Please try again.")
else:
    st.header(f"Welcome, {st.session_state.user_name}!")
    line_options = [
        f'🚄 Grandes Lignes',
        f'🚈 Banlieue de Tunis',
        f'🚆 Banlieue du Sahel'
    ]
    with next(get_db()) as db:
        stations_grandes_lignes = [station[0] for station in get_station_options(db)]
        stations_banlieue_tunis = [station[0] for station in get_banlieue_tunis_stations(db)]
        stations_banlieue_sahel = [station[0] for station in get_banlieue_sahel_stations(db)]

    selected_line_html = st.selectbox("Choisissez la ligne :", line_options)
    
    if selected_line_html == line_options[0]:
         selected_line = "Grandes Lignes"
    elif selected_line_html == line_options[1]:
         selected_line = "Banlieue de Tunis"
    elif selected_line_html == line_options[2]:
         selected_line = "Banlieue du Sahel"

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
        col1, col2 = st.columns(2)
        with col1:
            departure_station = st.selectbox("Gare de Départ :", departure_stations)
        with col2:
            arrival_station = st.selectbox("Gare d'Arrivée :", arrival_stations)

        transformed_departure_station = transform_station_name(departure_station)
        transformed_arrival_station = transform_station_name(arrival_station)

        if departure_station == arrival_station:
            st.warning("La gare de départ et d'arrivée ne peuvent pas être identiques.")
        else:
            departure_date = st.date_input("Date de départ :")

            def fetch_transports(origin, destination, date):
                formatted_date = date.strftime('%Y-%m-%d')
                payload = {
                    "origin": origin,
                    "destination": destination,
                    "date": formatted_date
                }
                response = requests.post(f"{API_URL}/get-transports/", json=payload)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                     try:
                        error_message = response.json()
                        if 'detail' in error_message:
                            st.info(error_message['detail'])
                        else:
                            st.info("No transports found for the specified criteria.")
                     except:
                        st.info("No transports found for the specified criteria.")
                     return []
                else:
                     try:
                         error_message = response.json()
                         st.error(f"Error fetching transports: {error_message.get('detail', response.text)}")
                     except:
                         st.error(f"Error fetching transports: {response.text}")
                     return []

            transports = fetch_transports(transformed_departure_station, transformed_arrival_station, departure_date)
            if transports:
                selected_transport_option = st.selectbox("Select a train:", 
                                                          options=[f"{t['departure_hour']} - {t['arrival_hour']}" for t in transports],
                                                          key="transport_select")
                selected_transport = next(t for t in transports if f"{t['departure_hour']} - {t['arrival_hour']}" == selected_transport_option)
                st.session_state.selected_travel = selected_transport
                
                button_selection = st.radio("Choose an option", ("Check Live Location", "Check Prices"))

                if button_selection == "Check Live Location":
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

                                col1, col2 = st.columns([1, 1])  
                                with col1:
                                    st.markdown(f"**Estimated Duration:** {directions_data.get('duration', 'Not available')}")
                                with col2:
                                    st.markdown(f"**Estimated Distance:** {directions_data.get('distance', 'Not available')}")
                            else:
                                st.warning(f"**No route found:** {directions_data['status']}")

                        else:
                            st.error(f"**Error fetching directions:** {response.text}")

                if button_selection == "Check Prices":
                    passenger_type = st.selectbox("Select Passenger Type:", ["Adult", "Student", "Child"], key="passenger_type")

                    if st.button("Check Prices"):
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

                            st.session_state.price_data = price_data

                            st.session_state.show_payment_page = True
                        else:
                            st.error(f"Error fetching price: {response.text}")


if st.session_state.get("show_payment_page", False):
    st.title("Payment Page")

    price_data = st.session_state.get("price_data")
    if price_data:
        st.write("### Price Details:")
        st.write(f"**Base Price:** {price_data['base_price']} TND")
        st.write(f"**Final Price:** {price_data['final_price']} TND")
        st.write(f"**Passenger Type:** {price_data['passenger_type']}")

        email = st.session_state.user_email

        if st.button("Pay Now"):
            try:
                amount_in_cents = int(float(price_data['final_price']) * 100)

                checkout_response = requests.post(
                    f"{API_URL}/create-checkout-session",
                    json={
                        "amount": amount_in_cents,
                        "currency": "usd",  
                        "email": email,  
                        "success_url": f"{SUCCESS_URL}?payment_id={{CHECKOUT_SESSION_ID}}", 
                    },
                )

                if checkout_response.status_code == 200:
                    checkout_session = checkout_response.json()
                    payment_url = checkout_session.get("payment_url")
                    print(f"Payment URL: {payment_url}")
                    st.session_state.email = checkout_session.get("email")
                    st.session_state.final_price = price_data['final_price']
                    st.session_state.show_payment_page = False


                    st.components.v1.html(
                        f"""
                        <script>
                            setTimeout(function() {{
                                window.open("{payment_url}", "_blank");
                            }}, 100); // Add a delay of 100ms
                        </script>
                        """,
                        height=0,
                    )
                    st.session_state.show_thank_you_page = True 

                else:
                    st.error(f"Failed to create payment: {checkout_response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("No price data found. Please go back and check prices again.")

def send_email(to_email, payment_id, final_price):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = "rayenrouaissi7@gmail.com"  
    subject = "Payment Confirmation"

    selected_travel = st.session_state.get("selected_travel")
    departure = selected_travel.get("origin") if selected_travel else "N/A"
    destination = selected_travel.get("destination") if selected_travel else "N/A"
    departure_hour = selected_travel.get("departure_hour") if selected_travel else "N/A"
    arrival_hour = selected_travel.get("arrival_hour") if selected_travel else "N/A"

    content = f"""
    Dear {st.session_state.user_name},

    Thank you for your recent purchase with SNCFT!

    We're pleased to confirm that your payment has been successfully processed. Here are the details:

    Payment ID: {payment_id}
    Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    Total Amount: {final_price} TND

    Travel Details:
    Departure: {departure}
    Destination: {destination}
    Departure Hour: {departure_hour}
    Arrival Hour: {arrival_hour}

    If you have any questions, please contact us.

    Best regards,
    The SNCFT Customer Support Team
    """
    message = Mail(from_email=from_email, to_emails=to_email, subject=subject, plain_text_content=content)

    try:
        response = sg.send(message)
        print(f"Email sent to {to_email}. Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")  
        return False


# Success page logic
if not st.session_state.show_success_message and st.session_state.show_thank_you_page:
    random_payment_id = random.randint(1, 1000)
    st.session_state.payment_id = random_payment_id
    st.session_state.show_success_message = True
    st.success(f"Payment successful! Payment ID: {st.session_state.payment_id}")

    if st.session_state.email and st.session_state.payment_id and st.session_state.final_price:
        if send_email(st.session_state.email, st.session_state.payment_id, st.session_state.final_price):
            st.success(f"An Email was sent to {st.session_state.email} confirming payment.")
        else:
            st.error("There was an error sending your email.")
elif st.session_state.show_success_message and st.session_state.show_thank_you_page:
    st.success(f"Payment successful! Payment ID: {st.session_state.payment_id}")
    if st.session_state.email and st.session_state.payment_id and st.session_state.final_price:
        if send_email(st.session_state.email, st.session_state.payment_id, st.session_state.final_price):
            st.success(f"An Email was sent to {st.session_state.email} confirming payment.")
        else:
            st.error("There was an error sending your email.")

if st.session_state.show_thank_you_page:
      st.title("Thank You!")
      st.write("Thank you for your purchase. Your transaction was successful.")
      st.write("We appreciate your trust in SNCFT. We hope you have a pleasant journey!")
      if st.button("Go Home"):
          st.session_state.show_thank_you_page = False
          st.session_state.show_success_message = False
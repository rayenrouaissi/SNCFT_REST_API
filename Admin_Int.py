import streamlit as st
from sqlalchemy.orm import Session
from database import get_db
from models import Admin
import requests
import pandas as pd
import altair as alt
from datetime import datetime
from typing import List  
import json

API_URL = "http://127.0.0.1:8000/travels/" 
EDIT_API_URL = "http://127.0.0.1:8000/travels/{travel_id}" 
DELETE_API_URL = "http://127.0.0.1:8000/travels/{travel_id}"  
PAYMENTS_API_URL = "http://127.0.0.1:8000/payments/"  
PAYMENT_BY_ID_API_URL = "http://127.0.0.1:8000/payments/{payment_id}"  
TRAVELERS_API_URL = "http://127.0.0.1:8000/get-travelers/"  
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False  
if "show_add_travel" not in st.session_state:
    st.session_state.show_add_travel = True  
if "show_edit_travel" not in st.session_state:
    st.session_state.show_edit_travel = False  
if "show_delete_travel" not in st.session_state:
    st.session_state.show_delete_travel = False 
if "show_fetch_travel" not in st.session_state:
    st.session_state.show_fetch_travel = False  
if "show_fetch_payments" not in st.session_state:
    st.session_state.show_fetch_payments = False
if "show_fetch_payment_by_id" not in st.session_state:
    st.session_state.show_fetch_payment_by_id = False
if "show_travelers" not in st.session_state:
     st.session_state.show_travelers = False
if "travelers_data" not in st.session_state:
    st.session_state.travelers_data = []
if "search_term" not in st.session_state:
    st.session_state.search_term = ""


st.image("SNCFT.png", caption="Welcome to SNCFT", use_container_width=True)

st.title("Admin Login Page")

if not st.session_state.logged_in:
    st.header("Admin Log In")
    email = st.text_input("Admin Email", placeholder="Enter your admin email address")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
    
    if st.button("Log In as Admin"):
        if not email or not password:
            st.error("Both email and password are required.")
        else:
            db: Session = next(get_db())  
            
            admin = db.query(Admin).filter(Admin.Email == email).first()  
            
            if admin and admin.Password == password:  
                st.session_state.logged_in = True
                st.session_state.user_name = admin.Email
                st.session_state.is_admin = True  
                st.success(f"Welcome back, Admin!")
            else:
                st.error("Invalid admin credentials. Please try again.")
else:
    if st.session_state.is_admin:
        st.header(f"Welcome, Admin!")

        st.write("Admin dashboard: You can manage the application here.")

        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
        
        with col1:
            if st.button("Add Travel", key="add_travel_button"):
                st.session_state.show_add_travel = True
                st.session_state.show_edit_travel = False
                st.session_state.show_delete_travel = False
                st.session_state.show_fetch_travel = False
                st.session_state.show_fetch_payments = False
                st.session_state.show_fetch_payment_by_id = False
                st.session_state.show_travelers = False
        
        with col2:
            if st.button("Edit Travel", key="edit_travel_button"):
                st.session_state.show_edit_travel = True
                st.session_state.show_add_travel = False
                st.session_state.show_delete_travel = False
                st.session_state.show_fetch_travel = False
                st.session_state.show_fetch_payments = False
                st.session_state.show_fetch_payment_by_id = False
                st.session_state.show_travelers = False

        with col3:
            if st.button("Delete Travel", key="delete_travel_button"):
                st.session_state.show_delete_travel = True
                st.session_state.show_add_travel = False
                st.session_state.show_edit_travel = False
                st.session_state.show_fetch_travel = False
                st.session_state.show_fetch_payments = False
                st.session_state.show_fetch_payment_by_id = False
                st.session_state.show_travelers = False

        with col4:
            if st.button("Travel Details", key="fetch_travel_button"):
                st.session_state.show_fetch_travel = True
                st.session_state.show_add_travel = False
                st.session_state.show_edit_travel = False
                st.session_state.show_delete_travel = False
                st.session_state.show_fetch_payments = False
                st.session_state.show_fetch_payment_by_id = False
                st.session_state.show_travelers = False
        with col5:
             if st.button("Payments", key="fetch_payments_button"):
                st.session_state.show_fetch_payments = True
                st.session_state.show_add_travel = False
                st.session_state.show_edit_travel = False
                st.session_state.show_delete_travel = False
                st.session_state.show_fetch_travel = False
                st.session_state.show_fetch_payment_by_id = False
                st.session_state.show_travelers = False

        with col6:
             if st.button("Payment by ID", key="fetch_payment_by_id_button"):
                st.session_state.show_fetch_payment_by_id = True
                st.session_state.show_fetch_payments = False
                st.session_state.show_add_travel = False
                st.session_state.show_edit_travel = False
                st.session_state.show_delete_travel = False
                st.session_state.show_fetch_travel = False
                st.session_state.show_travelers = False

        with col7:
             if st.button("Travelers", key="fetch_travelers_button"):
                st.session_state.show_travelers = True
                st.session_state.show_fetch_payment_by_id = False
                st.session_state.show_fetch_payments = False
                st.session_state.show_add_travel = False
                st.session_state.show_edit_travel = False
                st.session_state.show_delete_travel = False
                st.session_state.show_fetch_travel = False


        if st.session_state.show_add_travel:
            st.subheader("Add Travel Information")
            travel_id = st.number_input("Travel ID", min_value=1)
            origin = st.text_input("Origin")
            departure_hour = st.text_input("Departure Hour")
            destination = st.text_input("Destination")
            arrival_hour = st.text_input("Arrival Hour")
            date = st.text_input("Date (YYYY-MM-DD)")
            status = st.text_input("Status")
            current_loc = st.text_input("Current Location")
            price = st.number_input("Price", min_value=0, format="%d", value=0, step=1)

            if st.button("Add Travel", key="submit_add_travel"):
                travel_data = {
                    "travel_id": travel_id,
                    "origin": origin,
                    "departure_hour": departure_hour,
                    "destination": destination,
                    "arrival_hour": arrival_hour,
                    "date": date,
                    "status": status,
                    "current_loc": current_loc,
                    "price": int(price),  
                }

                try:
                    response = requests.post(API_URL, json=travel_data)
                    if response.status_code == 200:
                        st.success("Travel information added successfully!")
                    else:
                        st.error(f"Error adding travel: {response.text}")
                except Exception as e:
                    st.error(f"Error adding travel information: {e}")

        if st.session_state.show_edit_travel:
            st.subheader("Edit Travel Information")

            travel_id = st.number_input("Enter Travel ID to Edit", min_value=1, key="edit_travel_id_input")
            
            if travel_id:
                try:
                    response = requests.get(f"{EDIT_API_URL.format(travel_id=travel_id)}")
                    if response.status_code == 200:
                        travel = response.json()
                        
                        origin = st.text_input("Origin", value=travel["origin"])
                        departure_hour = st.text_input("Departure Hour", value=travel["departure_hour"])
                        destination = st.text_input("Destination", value=travel["destination"])
                        arrival_hour = st.text_input("Arrival Hour", value=travel["arrival_hour"])
                        date = st.text_input("Date (YYYY-MM-DD)", value=travel["date"])
                        status = st.text_input("Status", value=travel["status"])
                        current_loc = st.text_input("Current Location", value=travel["current_loc"])
                        price = st.number_input("Price", min_value=0, value=travel["price"], step=1)

                        if st.button("Save Changes", key="save_changes_button"):
                            updated_data = {
                                "origin": origin,
                                "departure_hour": departure_hour,
                                "destination": destination,
                                "arrival_hour": arrival_hour,
                                "date": date,
                                "status": status,
                                "current_loc": current_loc,
                                "price": int(price),  
                            }

                            try:
                                update_response = requests.put(f"{EDIT_API_URL.format(travel_id=travel_id)}", json=updated_data)
                                if update_response.status_code == 200:
                                    st.success("Travel information updated successfully!")
                                else:
                                    st.error(f"Error updating travel: {update_response.text}")
                            except Exception as e:
                                st.error(f"Error updating travel information: {e}")
                    else:
                        st.error("Travel not found.")
                except Exception as e:
                    st.error(f"Error fetching travel information: {e}")

        if st.session_state.show_delete_travel:
            st.subheader("Delete Travel Information")

            travel_id = st.number_input("Enter Travel ID to Delete", min_value=1, key="delete_travel_id_input")

            if st.button("Delete Travel", key="submit_delete_travel"):
                try:
                    delete_response = requests.delete(f"{DELETE_API_URL.format(travel_id=travel_id)}")
                    if delete_response.status_code == 200:
                        st.success(f"Travel with ID {travel_id} has been deleted successfully!")
                    else:
                        st.error(f"Error deleting travel: {delete_response.text}")
                except Exception as e:
                    st.error(f"Error deleting travel information: {e}")

        if st.session_state.show_fetch_travel:
            st.subheader("Fetch Travel Details")

            travel_id = st.number_input("Enter Travel ID to Fetch Details", min_value=1, key="fetch_travel_id_input")

            if st.button("Fetch Travel Details", key="submit_fetch_travel"):
                try:
                    response = requests.get(f"{EDIT_API_URL.format(travel_id=travel_id)}")
                    if response.status_code == 200:
                        travel = response.json()
                        st.write("### Travel Details")
                        st.write(f"**Travel ID:** {travel['travel_id']}")
                        st.write(f"**Origin:** {travel['origin']}")
                        st.write(f"**Departure Hour:** {travel['departure_hour']}")
                        st.write(f"**Destination:** {travel['destination']}")
                        st.write(f"**Arrival Hour:** {travel['arrival_hour']}")
                        st.write(f"**Date:** {travel['date']}")
                        st.write(f"**Status:** {travel['status']}")
                        st.write(f"**Current Location:** {travel['current_loc']}")
                        st.write(f"**Price:** {travel['price']}")
                    else:
                        st.error("Travel not found.")
                except Exception as e:
                    st.error(f"Error fetching travel information: {e}")

        if st.session_state.show_fetch_payments:
            st.subheader("All Payment Details")
            if st.button("Fetch Payments", key = "submit_fetch_payments"):
                try:
                    response = requests.get(PAYMENTS_API_URL)
                    if response.status_code == 200:
                        payments = response.json()
                        if payments:
                            df = pd.DataFrame(payments)
                            st.write("### All Payment Details")
                            st.dataframe(df)  
                            total_revenue = df['price'].sum()
                            st.write(f"**Total Revenue:** {total_revenue:.2f}")
                            
                            df['date'] = pd.to_datetime(df['date'])
                            df['date'] = df['date'].dt.date
                            payment_counts = df['date'].value_counts().sort_index().reset_index()
                            payment_counts.columns = ['Date', 'Number of Payments']

                            chart = alt.Chart(payment_counts).mark_bar().encode(
                                    x = alt.X('Date:T', axis=alt.Axis(labelAngle=-45)),  # Rotate labels
                                    y = alt.Y('Number of Payments:Q'),
                                    tooltip=['Date', 'Number of Payments']
                                ).properties(
                                    title='Number of Payments per Day'
                                )
                            st.altair_chart(chart, use_container_width=True)

                        else:
                            st.info("No payments found.")
                    else:
                        st.error(f"Error fetching payments: {response.text}")
                except Exception as e:
                    st.error(f"Error fetching payments: {e}")

        if st.session_state.show_fetch_payment_by_id:
            st.subheader("Fetch Payment by ID")
            payment_id = st.number_input("Enter Payment ID to Fetch Details", min_value=1, key="fetch_payment_id_input")
            if st.button("Fetch Payment Details", key = "submit_fetch_payment_by_id"):
                try:
                    response = requests.get(f"{PAYMENT_BY_ID_API_URL.format(payment_id=payment_id)}")
                    if response.status_code == 200:
                        payment = response.json()
                        st.write("### Payment Details")
                        st.write(f"**Payment ID:** {payment['payment_id']}")
                        st.write(f"**Username:** {payment['username']}")
                        st.write(f"**Departure:** {payment['departure']}")
                        st.write(f"**Destination:** {payment['destination']}")
                        st.write(f"**Date:** {payment['date']}")
                        st.write(f"**Departure Hour:** {payment['departure_hour']}")
                        st.write(f"**Arrival Hour:** {payment['arrival_hour']}")
                        st.write(f"**Price:** {payment['price']}")
                    elif response.status_code == 404:
                       st.error("Payment Not Found")
                    else:
                        st.error(f"Error fetching payment: {response.text}")
                except Exception as e:
                    st.error(f"Error fetching payment details: {e}")


        if st.session_state.show_travelers:
            st.subheader("Traveler Details")

            view_option = st.radio("Select View", ["All Travelers", "Search Traveler"], key="traveler_view_radio")

            if not st.session_state.travelers_data:
                try:
                    response = requests.get(TRAVELERS_API_URL)
                    if response.status_code == 200:
                       st.session_state.travelers_data = response.json()
                    else:
                         st.error(f"Error fetching travelers: {response.text}")
                except Exception as e:
                      st.error(f"Error fetching travelers data: {e}")

            if view_option == "All Travelers":
                if st.session_state.travelers_data:
                     df_travelers = pd.DataFrame(st.session_state.travelers_data)
                     st.dataframe(df_travelers)
            elif view_option == "Search Traveler":
                   
                st.session_state.search_term = st.text_input("Enter name or email to search", value=st.session_state.search_term)
                
                if st.button("Search", key="search_traveler_button"):
                   if st.session_state.search_term:
                       filtered_travelers = [
                        traveler for traveler in st.session_state.travelers_data 
                        if st.session_state.search_term.lower() in traveler['Name'].lower() or st.session_state.search_term.lower() in traveler['Email'].lower()
                        ]
                       if filtered_travelers:
                           df_filtered = pd.DataFrame(filtered_travelers)
                           st.dataframe(df_filtered)
                       else:
                            st.write("No travelers found matching the search criteria.")
                   else:
                       st.write("Please enter a search term.")



        # Log out button
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.is_admin = False
            st.session_state.show_add_travel = True
            st.session_state.show_edit_travel = False
            st.session_state.show_delete_travel = False
            st.session_state.show_fetch_travel = False
            st.session_state.show_fetch_payments = False
            st.session_state.show_fetch_payment_by_id = False
            st.session_state.show_travelers = False
            st.session_state.travelers_data = [] 
            st.success("You have been logged out.")
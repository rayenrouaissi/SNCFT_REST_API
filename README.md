# 🚄 SNCFT REST API

The **SNCFT REST API** is a comprehensive solution for the **Tunisian National Railway Company**. It provides users with real-time train schedules, travel prices, locations, and estimated arrival times while enabling administrators to manage train services efficiently. This project aims to modernize public transportation and improve the travel experience in Tunisia.

---

## 📋 Features

### 🔹 User Features
- **Travel Search:** 
  - Find train routes based on origin, destination, and date.
  - Get live updates on train locations and travel statuses.
- **Ticket Purchase:** 
  - Secure payments using **Stripe**.
  - Automatic ticket delivery via **Twilio SendGrid**.
- **Real-Time Updates:**
  - View train locations and estimated arrival times (ETAs) in real-time.

### 🔹 Admin Features
- **Travel Management:**
  - Add, update, or delete train schedules.
  - Track live train locations and manage statuses.
- **User & Transaction Monitoring:**
  - Access user lists and transaction histories.
- **Data Integration:**
  - Update train routes and locations using **GoMaps API**.

---

## 🛠️ Tech Stack

### 🔧 Backend
- **FastAPI:** A high-performance Python web framework for building APIs.
- **PostgreSQL:** A relational database for secure and efficient data storage.
- **SQLAlchemy:** ORM for seamless database interaction.

### 🌐 Frontend
- **Streamlit:** Simplified interface for travelers and admins.

### 🔗 APIs and Integrations
- **GoMaps API:** For real-time route calculations and travel updates.
- **Stripe API:** Secure payment processing for tickets.
- **Twilio SendGrid API:** For ticket email notifications.

---

## 📊 Database Design

### Database Tables:
1. **Users:** Stores user account details.
2. **Admins:** Stores admin credentials and permissions.
3. **Train Stations:** Contains station names and IDs for the **Grandes Lignes**, **Tunis**, and **Sahel** routes.
4. **Travel:** Tracks schedules, current locations, statuses, and prices.
5. **Payments:** Logs ticket purchases, payment IDs, amounts, and travel details.

---

## 🚀 How It Works

### 🔹 User Workflow:
1. Enter **origin**, **destination**, and **date** to search for trains.
2. View available travel options and ticket prices.
3. Purchase tickets securely using **Stripe**.
4. Receive tickets via email and track train locations in real time.

### 🔹 Admin Workflow:
1. Log in to add, edit, or delete travel records.
2. Update train locations using **GoMaps API**.
3. Monitor user transactions and manage ticketing data.

---

## 📦 Installation

### 🔹 Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- API keys for **GoMaps**, **Stripe**, and **SendGrid**

### 🔹 Steps
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/<your-repo-name>/sncft-rest-api.git
   cd sncft-rest-api

# SNCFT_REST_API
This project implements a REST API for the Tunisian National Railway Company (SNCFT), providing users with detailed information about train schedules, travel prices, exact locations, and estimated arrival times. It aims to enhance the travel experience for passengers and improve the administrative management of train services in Tunisia.

Features
User Features:
Travel Management:
Search for available trains by origin, destination, and date.
Check travel prices and schedules.
Track live train locations and status updates.
Ticket Purchase:
Secure online payment integration via Stripe.
Automatic ticket delivery through Twilio SendGrid email notifications.
Admin Features:
Travel Management:
Add, update, and delete travel records.
Manage train locations, schedules, and statuses.
User and Transaction Monitoring:
View the list of registered users.
Monitor transactions and payment histories.
Real-Time Train Updates:
Update train locations using GoMaps API.
Tech Stack
Backend:
FastAPI: High-performance framework for building REST APIs.
PostgreSQL: Relational database management system for storing user, train, and payment data.
SQLAlchemy: ORM for database interactions.
Frontend:
Streamlit: Interactive web interface for travelers and administrators.
APIs and Integrations:
GoMaps API: For calculating routes, distances, and durations between train locations and destinations.
Stripe API: For secure payment processing.
Twilio SendGrid API: For automated email ticket delivery.
Other Tools:
BeautifulSoup and Pandas: For web scraping and cleaning train station data.
Swagger and Postman: For API documentation and testing.

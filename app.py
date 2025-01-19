from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from datetime import date, time
from typing import List
import logging
import jwt
from sqlalchemy.orm import Session
from models import User, Payment
from database import SessionLocal, engine, get_db
import models
import requests
import stripe

app = FastAPI(title="SNCFT REST API")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Secret key and algorithm
SECRET_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

# OAuth2 token URL for login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str


# Function to hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Function to create a JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Sign-Up Endpoint

class UserSignUp(BaseModel):
    Name: str
    Email: str
    Password: str

    class Config:
        from_attributes = True

@app.post("/signup")
async def sign_up(user: UserSignUp, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.Email == user.Email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(user.Password)

        new_user = User(Name=user.Name, Email=user.Email, Password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User successfully signed up"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.Email == form_data.username).first()

        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(form_data.password, db_user.Password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": db_user.Email})

        return {"message": "Welcome back"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")




#gomap integration 
GOMAPS_API_KEY = "AlzaSymKvczgMI9EGqbNInHODoKbfiUQGMbzJPK"

class DirectionsResponse(BaseModel):
    origin: str
    destination: str
    distance: str
    duration: str
    status: str
    current_loc: str


    
def get_directions(origin: str, destination: str, travel_date: str, db: Session) -> DirectionsResponse:
    travel = db.query(models.Travel).filter(
        models.Travel.origin == origin,
        models.Travel.destination == destination,
        models.Travel.date == travel_date
    ).first()

    if not travel:
        raise HTTPException(
            status_code=404, 
            detail=f"Travel not found for origin '{origin}', destination '{destination}' on {travel_date}"
        )

    current_loc = travel.current_loc

    # Call the GoMaps API to get directions
    url = f"https://maps.gomaps.pro/maps/api/directions/json?origin={current_loc}&destination={destination}&key={GOMAPS_API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'routes' in data and len(data['routes']) > 0:
            route = data['routes'][0]
            leg = route['legs'][0]
            
            simplified_response = DirectionsResponse(
                origin=current_loc, 
                destination=destination,
                distance=leg['distance']['text'],
                duration=leg['duration']['text'],
                status='success',
                current_loc=current_loc 
            )
        else:
            simplified_response = DirectionsResponse(
                origin=current_loc,
                destination=destination,
                distance="N/A",
                duration="N/A",
                status="no route found",
                current_loc=current_loc  
            )
    else:
        simplified_response = DirectionsResponse(
            origin=current_loc,
            destination=destination,
            distance="N/A",
            duration="N/A",
            status="error in API request",
            current_loc=current_loc  
        )
    
    return simplified_response


@app.get("/get-directions/", response_model=DirectionsResponse)
def get_directions_endpoint(origin: str, destination: str, travel_date: str, db: Session = Depends(get_db)):
    return get_directions(origin, destination, travel_date, db)




# get price endpoint
# Fare calculation logic based on passenger type
def calculate_fare(base_price: float, passenger_type: str) -> float:
    if passenger_type == "Adult":
        return base_price 
    elif passenger_type == "Student":
        return base_price * 0.5  
    elif passenger_type == "Child":
        return base_price * 0.2  
    else:
        raise HTTPException(status_code=400, detail="Invalid passenger type. Choose 'Adult', 'Student', or 'Child'.")

# API endpoint to check ticket prices
@app.get("/check-price/")
def check_price(
    origin: str, destination: str, date: str, passenger_type: str, db: Session = Depends(get_db)
):
    travel = (
        db.query(models.Travel)
        .filter(
            models.Travel.origin == origin,
            models.Travel.destination == destination,
            models.Travel.date == date,
        )
        .first()
    )

    if not travel:
        raise HTTPException(
            status_code=404,
            detail=f"No travel record found for origin '{origin}', destination '{destination}' on {date}",
        )

    base_price = travel.price 

    try:
        final_price = calculate_fare(base_price, passenger_type)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    return {
        "message": f"Ticket price from {origin} to {destination} for {passenger_type} on {date}",
        "base_price": base_price,
        "final_price": round(final_price, 2),
        "passenger_type": passenger_type,
    }



# Stripe API key
stripe.api_key = "sk_test_51QiJ2c6e6iB3iVrFtnsxDZ52VzCEExSIZt3VrzHdQ3djy618N28ZQRzj3FgBJ3LQKxiIa458l1eHgEuhqhOj8KIl0016X1sO6B"  # Replace with your Stripe Secret Key


class CheckoutSessionRequest(BaseModel):
    amount: int
    currency: str
    email: str
    success_url: str
    quantity: int = 1 

# Endpoint to create a Checkout Session
@app.post("/create-checkout-session")
async def create_checkout_session(checkout_request: CheckoutSessionRequest):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": checkout_request.currency,
                        "product_data": {
                            "name": "Streamlit Payment",
                        },
                        "unit_amount": checkout_request.amount,  
                    },
                    "quantity": checkout_request.quantity,
                }
            ],
            mode="payment",
             success_url=checkout_request.success_url,  
            cancel_url="http://localhost:8501/cancel",  
            customer_email=checkout_request.email,
        )

        # Return the Checkout Session URL
        return {"id": session.id, "payment_url": session.url, "email":checkout_request.email, "final_price": checkout_request.amount/100, "quantity": checkout_request.quantity} # add final_price to response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class TravelCreate(BaseModel):
    travel_id: int
    origin: str
    departure_hour: str
    destination: str
    arrival_hour: str
    date: str
    status: str
    current_loc: str
    price: int

@app.post("/travels/")
def create_travel(
    travel: TravelCreate,  
    db: Session = Depends(get_db)
):
    try:
        new_travel = models.Travel(
            travel_id=travel.travel_id,
            origin=travel.origin,
            departure_hour=travel.departure_hour,
            destination=travel.destination,
            arrival_hour=travel.arrival_hour,
            date=travel.date,
            status=travel.status,
            current_loc=travel.current_loc,  
            price=travel.price,
        )
        
        db.add(new_travel)
        db.commit()
        db.refresh(new_travel)
        
        return new_travel
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding travel: {str(e)}")

@app.get("/travels/{travel_id}")
def get_travel(travel_id: int, db: Session = Depends(get_db)):
    travel = db.query(models.Travel).filter(models.Travel.travel_id == travel_id).first()
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    return travel


@app.put("/travels/{travel_id}")
def update_travel(
    travel_id: int,
    origin: str = None,
    departure_hour: str = None,
    destination: str = None,
    arrival_hour: str = None,
    date: str = None,
    status: str = None,
    current_loc: str = None,
    price: float = None,
    db: Session = Depends(get_db),
):
    travel = db.query(models.Travel).filter(models.Travel.travel_id == travel_id).first()
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")

    if origin is not None:
        travel.origin = origin
    if departure_hour is not None:
        travel.departure_hour = departure_hour
    if destination is not None:
        travel.destination = destination
    if arrival_hour is not None:
        travel.arrival_hour = arrival_hour
    if date is not None:
        travel.date = date
    if status is not None:
        travel.status = status
    if current_loc is not None:
        travel.current_loc = current_loc
    if price is not None:
        travel.price = price

    db.commit()  
    db.refresh(travel)  
   

@app.delete("/travels/{travel_id}")
def delete_travel(travel_id: int, db: Session = Depends(get_db)):
    travel = db.query(models.Travel).filter(models.Travel.travel_id == travel_id).first()
    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found")
    db.delete(travel)
    db.commit()
    return {"detail": f"Travel with ID {travel_id} has been deleted."}

# update price endpoint

@app.put("/update-price/")
def update_price(
    origin: str,
    destination: str,
    date: str,
    departure_hour: str,
    arrival_hour: str,
    new_price: float,
    db: Session = Depends(get_db),
):
    travel = db.query(models.Travel).filter(
        models.Travel.origin == origin,
        models.Travel.destination == destination,
        models.Travel.date == date,
        models.Travel.departure_hour == departure_hour,
        models.Travel.arrival_hour == arrival_hour
    ).first()

    if not travel:
        raise HTTPException(status_code=404, detail="Travel not found for the given parameters.")
    
    travel.price = new_price
    
    db.commit()
    db.refresh(travel)
    
    return {
        "message": f"Price updated successfully for the route from {origin} to {destination} on {date}.",
        "new_price": new_price
    }



class TransportRequest(BaseModel):
    origin: str
    destination: str
    date: str

class TransportResponse(BaseModel):
    travel_id: int
    origin: str
    departure_hour: str
    destination: str
    arrival_hour: str
    date: str
    status: str
    price: float
    
    
# Endpoint to retrieve possible transports
@app.post("/get-transports/", response_model=list[TransportResponse])
async def get_transports(transport_request: TransportRequest, db: Session = Depends(get_db)):
    try:
        travels = db.query(models.Travel).filter(
            models.Travel.origin == transport_request.origin,
            models.Travel.destination == transport_request.destination,
            models.Travel.date == transport_request.date
        ).all()
        
        if not travels:
            raise HTTPException(status_code=404, detail="No transports found for the specified criteria")

        transport_list = []
        for travel in travels:
            transport_list.append(
                TransportResponse(
                    travel_id=travel.travel_id,
                    origin=travel.origin,
                    departure_hour=travel.departure_hour,
                    destination=travel.destination,
                    arrival_hour=travel.arrival_hour,
                    date=travel.date.isoformat() if travel.date else None,  # Convert date to string
                    status=travel.status,
                    price=float(travel.price) if travel.price is not None else 0.0 # Ensure price is float and not none.
                )
        )
            
        return transport_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    


class PaymentCreate(BaseModel):
    payment_id: int
    user_name: str
    departure: str
    destination: str
    date: date
    departure_hour: time
    arrival_hour: time
    price: int

class PaymentResponse(BaseModel):
    id: int
    payment_id: int
    user_name: str
    departure: str
    destination: str
    date: date
    departure_hour: time
    arrival_hour: time
    price: int

    class Config:
        from_attributes = True

# POST endpoint to add a payment

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class PaymentCreate(BaseModel):
    payment_id: int
    username: str
    departure: str
    destination: str
    date: str  
    departure_hour: str
    arrival_hour: str
    price: int

class PaymentResponse(BaseModel):
    payment_id: int
    username: str
    departure: str
    destination: str
    date: str  
    departure_hour: str
    arrival_hour: str
    price: int

    class Config:
        from_attributes = True

# Endpoint to create a new payment
@app.post("/payments/", response_model=PaymentResponse, status_code=201)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    try:
        print("Received payment data:", payment.dict())

        existing_payment = db.query(Payment).filter(Payment.payment_id == payment.payment_id).first()
        if existing_payment:
            raise HTTPException(status_code=400, detail="Payment with this payment_id already exists")

        db_payment = Payment(
            payment_id=payment.payment_id,
            username=payment.username,
            departure=payment.departure,
            destination=payment.destination,
            date=payment.date,  
            departure_hour=payment.departure_hour,
            arrival_hour=payment.arrival_hour,
            price=payment.price
        )
        
        print("Database Payment object created:", db_payment.__dict__)

        db.add(db_payment)
        print("Payment object added to the session")

        db.commit()
        print("Database commit successful")

        db.refresh(db_payment)
        print("Database refresh successful, returning payment:", db_payment.__dict__)

        if isinstance(db_payment.date, date):
            db_payment.date = db_payment.date.isoformat()

        return db_payment  

    except HTTPException as e:
        print(f"Error: {e.detail}")
        raise e

    except Exception as e:
        print(f"Error creating payment: {type(e)}, {e}")
        db.rollback() 
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# Endpoint to get all payments
@app.get("/payments/", response_model=List[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    try:
        payments = db.query(Payment).all()
        print("Fetched payments from the database:", payments)

        for payment in payments:
            if isinstance(payment.date, date):
                payment.date = payment.date.isoformat()

        return payments  

    except Exception as e:
        print(f"Error fetching payments: {type(e)}, {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Endpoint to get a single payment by payment_id
@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    try:
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        print(f"Fetched payment with ID {payment_id}:", payment)

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if isinstance(payment.date, date):
            payment.date = payment.date.isoformat()

        return payment  # Return the payment

    except HTTPException as e:
        print(f"Error: {e.detail}")
        raise e

    except Exception as e:
        print(f"Error fetching payment: {type(e)}, {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

class UserResponse(BaseModel):
    id: int
    Name: str
    Email: str

    class Config:
        from_attributes = True

# Endpoint to get all users
class UserResponse(BaseModel):
    Name: str
    Email: str

    class Config:
        from_attributes = True

@app.get("/get-travelers/", response_model=List[UserResponse])
def get_travelers(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        user_responses = [
            UserResponse(Name=user.Name, Email=user.Email)
            for user in users
        ]
        return user_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
from sqlalchemy import Column, Integer, String, Float, Date, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"  
    Email = Column(String, primary_key=True, index=True)
    Name = Column(String, index=True)
    Password = Column(String)

class Admin(Base):
    __tablename__ = 'Admin'

    Email = Column(String, unique=True, index=True, primary_key=True)  
    Password = Column(String)

# Define the Train Station GL model
class TrainStationGL(Base):
    __tablename__ = 'Train Station GL' 

    Station_ID = Column(Integer, primary_key=True, index=True)  
    Station_Name = Column(String, index=True)  

class TrainStationBT(Base):
    __tablename__ = 'Train Station BT'

    Station_ID = Column(Integer, primary_key=True, index=True)  
    Station_Name = Column(String, index=True)  

class TrainStationBS(Base):
    __tablename__ = 'Train Station BS'

    Station_ID = Column(Integer, primary_key=True, index=True)  
    Station_Name = Column(String, index=True)  


class Travel(Base):
    __tablename__ = "Travel"
    travel_id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    departure_hour = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    arrival_hour = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    current_loc = Column(String, nullable=False)
    price = Column(Integer)


class Payment(Base):
    __tablename__ = 'Payment'  
    
    payment_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    departure = Column(String)
    destination = Column(String)
    date = Column(Date)
    departure_hour = Column(String)
    arrival_hour = Column(String)
    price = Column(Integer)
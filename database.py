from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import TrainStationGL, TrainStationBS, TrainStationBT
from sqlalchemy.orm import Session


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:rayen2002@localhost:5432/postgres?client_encoding=utf8"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_station_options(db: Session):
    stations = db.query(TrainStationGL.Station_Name, TrainStationGL.Station_ID).all()
    return [(station[0], station[1]) for station in stations]



def get_banlieue_tunis_stations(db: Session):
    stations = db.query(TrainStationBT.Station_Name, TrainStationBT.Station_ID).all()
    return [(station[0], station[1]) for station in stations]

def get_banlieue_sahel_stations(db: Session):
    stations = db.query(TrainStationBS.Station_Name, TrainStationBS.Station_ID).all()
    return [(station[0], station[1]) for station in stations]




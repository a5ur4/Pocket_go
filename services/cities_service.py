from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.cities_model import CitiesModel
import database.schemas.cities_schema as schemas

def getAllCities(db: Session):
    return db.query(CitiesModel).all()

def getCityById(db: Session, city_id: str):
    return db.query(CitiesModel).filter(CitiesModel.id == city_id).first()

def getCityByName(db: Session, name: str):
    return db.query(CitiesModel).filter(CitiesModel.name == name).first()

def createCity(db: Session, city: schemas.CitiesCreate):
    try:
        db_city = CitiesModel(
            name=city.name,
            state=city.state,
            country=city.country
        )
        db.add(db_city)
        db.commit()
        db.refresh(db_city)
        return db_city
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateCity(db: Session, city_id: str, city: schemas.CitiesUpdate):
    try:
        db_city = db.query(CitiesModel).filter(CitiesModel.id == city_id).first()
        if not db_city:
            return None
        
        update_data = city.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_city, field, value)
        
        db.commit()
        db.refresh(db_city)
        return db_city
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteCity(db: Session, city_id: str):
    try:
        db_city = db.query(CitiesModel).filter(CitiesModel.id == city_id).first()
        if not db_city:
            return False
        
        db.delete(db_city)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e


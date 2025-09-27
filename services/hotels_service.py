from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.hotels_model import HotelsModel
import database.schemas.hotels_schema as schemas

def getAllHotels(db: Session):
    return db.query(HotelsModel).all()

def getHotelById(db: Session, hotel_id: str):
    return db.query(HotelsModel).filter(HotelsModel.id == hotel_id).first()

def getHotelsByCityId(db: Session, city_id: str):
    return db.query(HotelsModel).filter(HotelsModel.city_id == city_id).all()

def getPromotedHotels(db: Session):
    return db.query(HotelsModel).filter(HotelsModel.is_promoted == True).all()

def createHotel(db: Session, hotel: schemas.HotelsCreate):
    try:
        db_hotel = HotelsModel(
            name=hotel.name,
            description=hotel.description,
            type=hotel.type,
            address=hotel.address,
            city_id=hotel.city_id,
            location=hotel.location,
            phone=hotel.phone,
            email=hotel.email,
            website=hotel.website,
            is_promoted=hotel.is_promoted
        )
        db.add(db_hotel)
        db.commit()
        db.refresh(db_hotel)
        return db_hotel
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateHotel(db: Session, hotel_id: str, hotel: schemas.HotelsUpdate):
    try:
        db_hotel = db.query(HotelsModel).filter(HotelsModel.id == hotel_id).first()
        if not db_hotel:
            return None
        
        update_data = hotel.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_hotel, field, value)
        
        db.commit()
        db.refresh(db_hotel)
        return db_hotel
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteHotel(db: Session, hotel_id: str):
    try:
        db_hotel = db.query(HotelsModel).filter(HotelsModel.id == hotel_id).first()
        if not db_hotel:
            return False
        
        db.delete(db_hotel)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
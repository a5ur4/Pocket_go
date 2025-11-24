from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.hotel_details_model import HotelDetailsModel
import database.schemas.hotel_details_schema as schemas

def getAllHotelDetails(db: Session):
    return db.query(HotelDetailsModel).all()

def getHotelDetailsById(db: Session, detail_id: str):
    return db.query(HotelDetailsModel).filter(HotelDetailsModel.id == detail_id).first()

def getHotelDetailsByHotelId(db: Session, hotel_id: str):
    return db.query(HotelDetailsModel).filter(HotelDetailsModel.hotel_id == hotel_id).first()

def createHotelDetails(db: Session, details: schemas.HotelDetailsCreate):
    try:
        db_details = HotelDetailsModel(
            hotel_id=details.hotel_id,
            animals_allowed=details.animals_allowed,
            wifi_available=details.wifi_available,
            breakfast_included=details.breakfast_included,
            gym_available=details.gym_available,
            parking_available=details.parking_available
        )
        db.add(db_details)
        db.commit()
        db.refresh(db_details)
        return db_details
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateHotelDetails(db: Session, detail_id: str, details: schemas.HotelDetailsUpdate):
    try:
        db_details = db.query(HotelDetailsModel).filter(HotelDetailsModel.id == detail_id).first()
        if not db_details:
            return None
        
        update_data = details.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_details, field, value)
        
        db.commit()
        db.refresh(db_details)
        return db_details
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteHotelDetails(db: Session, detail_id: str):
    try:
        db_details = db.query(HotelDetailsModel).filter(HotelDetailsModel.id == detail_id).first()
        if not db_details:
            return False
        
        db.delete(db_details)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
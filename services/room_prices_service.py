from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.room_prices_model import RoomPricesModel
import database.schemas.room_prices_schema as schemas

def getAllRoomPrices(db: Session):
    return db.query(RoomPricesModel).all()

def getRoomPriceById(db: Session, room_price_id: str):
    return db.query(RoomPricesModel).filter(RoomPricesModel.id == room_price_id).first()

def getRoomPricesByRoomTypeId(db: Session, room_type_id: str):
    return db.query(RoomPricesModel).filter(RoomPricesModel.room_type_id == room_type_id).all()

def getRoomPricesByRatePlanId(db: Session, rate_plan_id: str):
    return db.query(RoomPricesModel).filter(RoomPricesModel.rate_plan_id == rate_plan_id).all()

def getByPriceRange(db: Session, min_price: float, max_price: float):
    return db.query(RoomPricesModel).filter(
        RoomPricesModel.amount >= min_price,
        RoomPricesModel.amount <= max_price
    ).all()

def createRoomPrice(db: Session, room_price: schemas.RoomPricesCreate):
    try:
        db_room_price = RoomPricesModel(
            room_type_id=room_price.room_type_id,
            rate_plan_id=room_price.rate_plan_id,
            amount=room_price.amount,
            currency=room_price.currency,
            days_of_week=room_price.days_of_week
        )
        db.add(db_room_price)
        db.commit()
        db.refresh(db_room_price)
        return db_room_price
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateRoomPrice(db: Session, room_price_id: str, room_price: schemas.RoomPricesUpdate):
    try:
        db_room_price = db.query(RoomPricesModel).filter(RoomPricesModel.id == room_price_id).first()
        if not db_room_price:
            return None
        
        update_data = room_price.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_room_price, field, value)
        
        db.commit()
        db.refresh(db_room_price)
        return db_room_price
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteRoomPrice(db: Session, room_price_id: str):
    try:
        db_room_price = db.query(RoomPricesModel).filter(RoomPricesModel.id == room_price_id).first()
        if not db_room_price:
            return False
        
        db.delete(db_room_price)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
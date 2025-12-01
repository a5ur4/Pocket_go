from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.room_types_model import RoomTypesModel
import database.schemas.room_types_schema as schemas

def getAllRoomTypes(db: Session):
    return db.query(RoomTypesModel).all()

def getRoomTypeById(db: Session, room_type_id: str):
    return db.query(RoomTypesModel).filter(RoomTypesModel.id == room_type_id).first()

def getRoomTypesByHotelId(db: Session, hotel_id: str):
    return db.query(RoomTypesModel).filter(RoomTypesModel.hotel_id == hotel_id).all()

def createRoomType(db: Session, room_type: schemas.RoomTypesCreate):
    try:
        db_room_type = RoomTypesModel(
            hotel_id=room_type.hotel_id,
            name=room_type.name,
            description=room_type.description,
            capacity=room_type.capacity,
            image_url=room_type.image_url
        )
        db.add(db_room_type)
        db.commit()
        db.refresh(db_room_type)
        return db_room_type
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateRoomType(db: Session, room_type_id: str, room_type: schemas.RoomTypesUpdate):
    try:
        db_room_type = db.query(RoomTypesModel).filter(RoomTypesModel.id == room_type_id).first()
        if not db_room_type:
            return None
        
        update_data = room_type.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_room_type, field, value)
        
        db.commit()
        db.refresh(db_room_type)
        return db_room_type
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteRoomType(db: Session, room_type_id: str):
    try:
        db_room_type = db.query(RoomTypesModel).filter(RoomTypesModel.id == room_type_id).first()
        if not db_room_type:
            return False
        
        db.delete(db_room_type)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
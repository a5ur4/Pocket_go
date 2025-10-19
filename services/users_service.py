from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.users_model import UsersModel
import database.schemas.users_schema as schemas

def getAllUsers(db: Session):
    return db.query(UsersModel).all()

def getUserById(db: Session, user_id: str):
    return db.query(UsersModel).filter(UsersModel.id == user_id).first()

def getUserByPhone(db: Session, phone: str):
    return db.query(UsersModel).filter(UsersModel.phone == phone).first()

def getUserByTelegramId(db: Session, telegram_id: str):
    return db.query(UsersModel).filter(UsersModel.telegram_id == telegram_id).first()

def createUser(db: Session, user: schemas.UsersCreate):
    try:
        db_user = UsersModel(
            phone=user.phone,
            telegram_id=user.telegram_id,
            first_location=user.first_location
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateUser(db: Session, user_id: str, user: schemas.UsersUpdate):
    try:
        db_user = db.query(UsersModel).filter(UsersModel.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteUser(db: Session, user_id: str):
    try:
        db_user = db.query(UsersModel).filter(UsersModel.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from models.user_searches_model import UserSearchesModel
import database.schemas.user_searches_schema as schemas

def getAllUserSearches(db: Session):
    return db.query(UserSearchesModel).all()

def getUserSearchById(db: Session, search_id: str):
    return db.query(UserSearchesModel).filter(UserSearchesModel.id == search_id).first()

def getUserSearchesByUserIdentifier(db: Session, user_identifier: str):
    return db.query(UserSearchesModel).filter(UserSearchesModel.user_identifier == user_identifier).all()

def getRecentSearches(db: Session, days: int = 7):
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    return db.query(UserSearchesModel).filter(UserSearchesModel.created_at >= cutoff_date).all()

def createUserSearch(db: Session, search: schemas.UserSearchesCreate):
    try:
        db_search = UserSearchesModel(
            user_identifier=search.user_identifier,
            search_location=search.search_location
        )
        db.add(db_search)
        db.commit()
        db.refresh(db_search)
        return db_search
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateUserSearch(db: Session, search_id: str, search: schemas.UserSearchesUpdate):
    try:
        db_search = db.query(UserSearchesModel).filter(UserSearchesModel.id == search_id).first()
        if not db_search:
            return None
        
        update_data = search.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_search, field, value)
        
        db.commit()
        db.refresh(db_search)
        return db_search
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteUserSearch(db: Session, search_id: str):
    try:
        db_search = db.query(UserSearchesModel).filter(UserSearchesModel.id == search_id).first()
        if not db_search:
            return False
        
        db.delete(db_search)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
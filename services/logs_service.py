from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from models.logs_model import LogsModel
import database.schemas.logs_schema as schemas

def getAllLogs(db: Session):
    return db.query(LogsModel).all()

def getLogById(db: Session, log_id: str):
    return db.query(LogsModel).filter(LogsModel.id == log_id).first()

def getLogsByAction(db: Session, action: str):
    return db.query(LogsModel).filter(LogsModel.action == action).all()

def getLogsByEntity(db: Session, entity: str, entity_id: str = None):
    query = db.query(LogsModel).filter(LogsModel.entity == entity)
    if entity_id:
        query = query.filter(LogsModel.entity_id == entity_id)
    return query.all()

def getRecentLogs(db: Session, hours: int = 24):
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(LogsModel).filter(LogsModel.timestamp >= cutoff_time).all()

def createLog(db: Session, log: schemas.LogsCreate):
    try:
        db_log = LogsModel(
            action=log.action,
            entity=log.entity,
            entity_id=log.entity_id,
            details=log.details
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteOldLogs(db: Session, days: int = 30):
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = db.query(LogsModel).filter(LogsModel.timestamp < cutoff_date).delete()
        db.commit()
        return deleted_count
    except SQLAlchemyError as e:
        db.rollback()
        raise e
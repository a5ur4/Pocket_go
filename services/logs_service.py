from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Optional

from models.logs_model import LogsModel
import database.schemas.logs_schema as schemas

def getAllLogs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(LogsModel).order_by(desc(LogsModel.timestamp)).offset(skip).limit(limit).all()

def getLogById(db: Session, log_id: str):
    return db.query(LogsModel).filter(LogsModel.id == log_id).first()

def getLogsByAction(db: Session, action: str, skip: int = 0, limit: int = 100):
    return db.query(LogsModel).filter(LogsModel.action == action).order_by(desc(LogsModel.timestamp)).offset(skip).limit(limit).all()

def getLogsByActions(db: Session, actions: List[str], skip: int = 0, limit: int = 100):
    """Get logs by multiple actions"""
    return db.query(LogsModel).filter(LogsModel.action.in_(actions)).order_by(desc(LogsModel.timestamp)).offset(skip).limit(limit).all()

def getRecentLogs(db: Session, hours: int = 24, skip: int = 0, limit: int = 100):
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(LogsModel).filter(LogsModel.timestamp >= cutoff_time).order_by(desc(LogsModel.timestamp)).offset(skip).limit(limit).all()

def getLogsByDateRange(db: Session, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100):
    """Get logs within a specific date range"""
    return db.query(LogsModel).filter(
        and_(LogsModel.timestamp >= start_date, LogsModel.timestamp <= end_date)
    ).order_by(desc(LogsModel.timestamp)).offset(skip).limit(limit).all()

def getErrorLogs(db: Session, hours: int = 24, skip: int = 0, limit: int = 100):
    """Get error logs (API errors, application errors, etc.)"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    error_actions = ['API_ERROR', 'APPLICATION_ERROR', 'DATABASE_ERROR', 'API_CLIENT_ERROR']
    return db.query(LogsModel).filter(
        and_(
            LogsModel.timestamp >= cutoff_time,
            LogsModel.action.in_(error_actions)
        )
    ).order_by(desc(LogsModel.timestamp)).offset(skip).limit(limit).all()

def getTelegramBotLogs(db: Session, hours: int = 24, skip: int = 0, limit: int = 100):
    """Get telegram bot related logs"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(LogsModel).filter(
        and_(
            LogsModel.timestamp >= cutoff_time,
            LogsModel.action.like('TELEGRAM_%')
        )
    ).order_by(desc(LogsModel.timestamp)).offset(skip).limit(limit).all()

def getHotelSearchLogs(db: Session, hours: int = 24, skip: int = 0, limit: int = 100):
    """Get hotel search related logs"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(LogsModel).filter(
        and_(
            LogsModel.timestamp >= cutoff_time,
            LogsModel.action == 'HOTEL_SEARCH'
        )
    ).order_by(desc(LogsModel.timestamp)).offset(skip).limit(limit).all()

def getLogStats(db: Session, hours: int = 24):
    """Get basic statistics about logs"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    total_logs = db.query(LogsModel).filter(LogsModel.timestamp >= cutoff_time).count()
    error_logs = db.query(LogsModel).filter(
        and_(
            LogsModel.timestamp >= cutoff_time,
            LogsModel.action.in_(['API_ERROR', 'APPLICATION_ERROR', 'DATABASE_ERROR'])
        )
    ).count()
    
    api_requests = db.query(LogsModel).filter(
        and_(
            LogsModel.timestamp >= cutoff_time,
            LogsModel.action == 'API_REQUEST'
        )
    ).count()
    
    telegram_actions = db.query(LogsModel).filter(
        and_(
            LogsModel.timestamp >= cutoff_time,
            LogsModel.action.like('TELEGRAM_%')
        )
    ).count()
    
    hotel_searches = db.query(LogsModel).filter(
        and_(
            LogsModel.timestamp >= cutoff_time,
            LogsModel.action == 'HOTEL_SEARCH'
        )
    ).count()
    
    return {
        "total_logs": total_logs,
        "error_logs": error_logs,
        "api_requests": api_requests,
        "telegram_actions": telegram_actions,
        "hotel_searches": hotel_searches,
        "period_hours": hours
    }

def createLog(db: Session, log: schemas.LogsCreate):
    try:
        db_log = LogsModel(
            action=log.action,
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
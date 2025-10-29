import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import Request

from database.engine_db import SessionLocal
from services.logs_service import createLog
from database.schemas.logs_schema import LogsCreate

logger = logging.getLogger(__name__)

class APILogger:
    """Utility class for logging specific events in the API"""
    
    @staticmethod
    def log_user_action(
        action: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log user-specific actions"""
        db: Session = SessionLocal()
        try:
            log_details = details or {}
            
            if user_id:
                log_details["user_id"] = user_id
            
            if request:
                log_details.update({
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "path": request.url.path
                })
            
            log_create = LogsCreate(
                action=f"USER_{action}",
                details=log_details
            )
            
            createLog(db, log_create)
            
        except Exception as e:
            logger.error(f"Failed to log user action: {e}")
        finally:
            db.close()
    
    @staticmethod
    def log_telegram_bot_action(
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log Telegram bot interactions"""
        db: Session = SessionLocal()
        try:
            log_details = details or {}
            
            if user_id:
                log_details["telegram_user_id"] = user_id
            if username:
                log_details["telegram_username"] = username
            
            log_create = LogsCreate(
                action=f"TELEGRAM_{action}",
                details=log_details
            )
            
            createLog(db, log_create)
            
        except Exception as e:
            logger.error(f"Failed to log telegram action: {e}")
        finally:
            db.close()
    
    @staticmethod
    def log_hotel_search(
        latitude: float,
        longitude: float,
        results_count: int,
        search_type: str = "nearby",
        hotel_type: Optional[str] = None,
        max_distance_km: Optional[int] = None,
        user_id: Optional[str] = None,
        telegram_user_id: Optional[int] = None
    ):
        """Log hotel search operations"""
        db: Session = SessionLocal()
        try:
            details = {
                "latitude": latitude,
                "longitude": longitude,
                "results_count": results_count,
                "search_type": search_type,
                "max_distance_km": max_distance_km
            }
            
            if hotel_type:
                details["hotel_type"] = hotel_type
            if user_id:
                details["user_id"] = user_id
            if telegram_user_id:
                details["telegram_user_id"] = telegram_user_id
            
            log_create = LogsCreate(
                action="HOTEL_SEARCH",
                details=details
            )
            
            createLog(db, log_create)
            
        except Exception as e:
            logger.error(f"Failed to log hotel search: {e}")
        finally:
            db.close()
    
    @staticmethod
    def log_error(
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log application errors"""
        db: Session = SessionLocal()
        try:
            details = {
                "error_type": error_type,
                "error_message": error_message
            }
            
            if context:
                details["context"] = context
            
            if request:
                details.update({
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": request.client.host if request.client else "unknown"
                })
            
            log_create = LogsCreate(
                action="APPLICATION_ERROR",
                details=details
            )
            
            createLog(db, log_create)
            
        except Exception as e:
            logger.error(f"Failed to log application error: {e}")
        finally:
            db.close()
    
    @staticmethod
    def log_database_operation(
        operation: str,
        table: str,
        record_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log database operations"""
        db: Session = SessionLocal()
        try:
            details = {
                "operation": operation,  # CREATE, READ, UPDATE, DELETE
                "table": table,
                "success": success
            }
            
            if record_id:
                details["record_id"] = record_id
            if error_message:
                details["error_message"] = error_message
            
            action = "DATABASE_SUCCESS" if success else "DATABASE_ERROR"
            
            log_create = LogsCreate(
                action=action,
                details=details
            )
            
            createLog(db, log_create)
            
        except Exception as e:
            logger.error(f"Failed to log database operation: {e}")
        finally:
            db.close()
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

import services.logs_service as services
import database.schemas.logs_schema as schemas
from database.engine_db import get_db

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.LogsResponse])
def get_logs(
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    db: Session = Depends(get_db)
):
    """Get all logs with pagination"""
    logs = services.getAllLogs(db, skip=skip, limit=limit)
    return logs

@router.get("/stats/", response_model=dict)
def get_log_stats(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
    db: Session = Depends(get_db)
):
    """Get log statistics for the specified time period"""
    stats = services.getLogStats(db, hours=hours)
    return stats

@router.get("/errors/", response_model=list[schemas.LogsResponse])
def get_error_logs(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get error logs from the specified time period"""
    logs = services.getErrorLogs(db, hours=hours, skip=skip, limit=limit)
    return logs

@router.get("/telegram/", response_model=list[schemas.LogsResponse])
def get_telegram_logs(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get Telegram bot logs from the specified time period"""
    logs = services.getTelegramBotLogs(db, hours=hours, skip=skip, limit=limit)
    return logs

@router.get("/hotel-searches/", response_model=list[schemas.LogsResponse])
def get_hotel_search_logs(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get hotel search logs from the specified time period"""
    logs = services.getHotelSearchLogs(db, hours=hours, skip=skip, limit=limit)
    return logs

@router.get("/{log_id}", response_model=schemas.LogsResponse)
def get_log(log_id: str, db: Session = Depends(get_db)):
    """Get a specific log by ID"""
    log = services.getLogById(db, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.get("/action/{action}", response_model=list[schemas.LogsResponse])
def get_logs_by_action(
    action: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get logs by specific action type"""
    logs = services.getLogsByAction(db, action, skip=skip, limit=limit)
    return logs

@router.get("/recent/", response_model=list[schemas.LogsResponse])
def get_recent_logs(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get recent logs from the specified time period"""
    logs = services.getRecentLogs(db, hours=hours, skip=skip, limit=limit)
    return logs

@router.post("/", response_model=schemas.LogsResponse)
def create_log(log: schemas.LogsCreate, db: Session = Depends(get_db)):
    """Create a new log entry"""
    return services.createLog(db, log)

@router.delete("/old/", response_model=dict)
def delete_old_logs(
    days: int = Query(30, ge=1, le=365, description="Delete logs older than this many days"),
    db: Session = Depends(get_db)
):
    """Delete old logs to free up database space"""
    deleted_count = services.deleteOldLogs(db, days)
    return {"detail": f"Deleted {deleted_count} old logs older than {days} days"}

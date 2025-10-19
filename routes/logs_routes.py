from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import services.logs_service as services
import database.schemas.logs_schema as schemas
from database.engine_db import get_db

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.LogsResponse])
def get_logs(db: Session = Depends(get_db)):
    logs = services.getAllLogs(db)
    return logs

@router.get("/{log_id}", response_model=schemas.LogsResponse)
def get_log(log_id: str, db: Session = Depends(get_db)):
    log = services.getLogById(db, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.get("/action/{action}", response_model=list[schemas.LogsResponse])
def get_logs_by_action(action: str, db: Session = Depends(get_db)):
    logs = services.getLogsByAction(db, action)
    return logs

@router.get("/entity/{entity}", response_model=list[schemas.LogsResponse])
def get_logs_by_entity(entity: str, entity_id: str = None, db: Session = Depends(get_db)):
    logs = services.getLogsByEntity(db, entity, entity_id)
    return logs

@router.get("/recent/", response_model=list[schemas.LogsResponse])
def get_recent_logs(hours: int = 24, db: Session = Depends(get_db)):
    logs = services.getRecentLogs(db, hours)
    return logs

@router.post("/", response_model=schemas.LogsResponse)
def create_log(log: schemas.LogsCreate, db: Session = Depends(get_db)):
    return services.createLog(db, log)

@router.delete("/old/", response_model=dict)
def delete_old_logs(days: int = 30, db: Session = Depends(get_db)):
    deleted_count = services.deleteOldLogs(db, days)
    return {"detail": f"Deleted {deleted_count} old logs"}

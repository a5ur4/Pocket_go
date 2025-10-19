from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import database.schemas.users_schema as schemas
import services.users_service as services
from database.engine_db import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.UsersResponse])
def get_users(db: Session = Depends(get_db)):
    users = services.getAllUsers(db)
    return users

@router.get("/{user_id}", response_model=schemas.UsersResponse)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    user = services.getUserById(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/phone/{phone}", response_model=schemas.UsersResponse)
def get_user_by_phone(phone: str, db: Session = Depends(get_db)):
    user = services.getUserByPhone(db, phone)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/telegram/{telegram_id}", response_model=schemas.UsersResponse)
def get_user_by_telegram_id(telegram_id: str, db: Session = Depends(get_db)):
    user = services.getUserByTelegramId(db, telegram_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=schemas.UsersResponse)
def create_user(user: schemas.UsersCreate, db: Session = Depends(get_db)):
    return services.createUser(db, user)

@router.put("/{user_id}", response_model=schemas.UsersResponse)
def update_user(user_id: str, user: schemas.UsersUpdate, db: Session = Depends(get_db)):
    updated_user = services.updateUser(db, user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    success = services.deleteUser(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import database.schemas.user_searches_schema as schemas
import services.user_searches_service as services
from database.engine_db import get_db

router = APIRouter(
    prefix="/user_searches",
    tags=["User Searches"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.UserSearchesResponse])
def get_user_searches(db: Session = Depends(get_db)):
    user_searches = services.getAllUserSearches(db)
    return user_searches

@router.get("/{search_id}", response_model=schemas.UserSearchesResponse)
def get_user_search_by_id(search_id: str, db: Session = Depends(get_db)):
    user_search = services.getUserSearchById(db, search_id)
    if user_search is None:
        raise HTTPException(status_code=404, detail="User search not found")
    return user_search

@router.get("/user/{user_identifier}", response_model=list[schemas.UserSearchesResponse])
def get_user_searches_by_user_identifier(user_identifier: str, db: Session = Depends(get_db)):
    user_searches = services.getUserSearchesByUserIdentifier(db, user_identifier)
    return user_searches

@router.get("/recent/", response_model=list[schemas.UserSearchesResponse])
def get_recent_searches(days: int = 7, db: Session = Depends(get_db)):
    recent_searches = services.getRecentSearches(db, days)
    return recent_searches

@router.post("/", response_model=schemas.UserSearchesResponse)
def create_user_search(search: schemas.UserSearchesCreate, db: Session = Depends(get_db)):
    return services.createUserSearch(db, search)

@router.put("/{search_id}", response_model=schemas.UserSearchesResponse)
def update_user_search(search_id: str, search: schemas.UserSearchesUpdate, db: Session = Depends(get_db)):
    updated_search = services.updateUserSearch(db, search_id, search)
    if updated_search is None:
        raise HTTPException(status_code=404, detail="User search not found")
    return updated_search

@router.delete("/{search_id}", response_model=dict)
def delete_user_search(search_id: str, db: Session = Depends(get_db)):
    success = services.deleteUserSearch(db, search_id)
    if not success:
        raise HTTPException(status_code=404, detail="User search not found")
    return {"detail": "User search deleted successfully"}
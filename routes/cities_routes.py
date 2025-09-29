from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import database.schemas.cities_schema as schemas
import services.cities_service as services
from database.engine_db import get_db

router = APIRouter(
    prefix="/cities",
    tags=["Cities"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.CitiesResponse])
def read_cities(db: Session = Depends(get_db)):
    cities = services.getAllCities(db)
    return cities

@router.get("/{city_id}", response_model=schemas.CitiesResponse)
def read_city(city_id: str, db: Session = Depends(get_db)):
    city = services.getCityById(db, city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return city

@router.post("/", response_model=schemas.CitiesResponse)
def create_city(city: schemas.CitiesCreate, db: Session = Depends(get_db)):
    return services.createCity(db, city)

@router.put("/{city_id}", response_model=schemas.CitiesResponse)
def update_city(city_id: str, city: schemas.CitiesUpdate, db: Session = Depends(get_db)):
    updated_city = services.updateCity(db, city_id, city)
    if updated_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return updated_city

@router.delete("/{city_id}", response_model=dict)
def delete_city(city_id: str, db: Session = Depends(get_db)):
    success = services.deleteCity(db, city_id)
    if not success:
        raise HTTPException(status_code=404, detail="City not found")
    return {"detail": "City deleted successfully"}
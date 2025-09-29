from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import database.schemas.hotels_schema as schemas
import services.hotels_service as services
from database.engine_db import get_db

router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.HotelsResponse])
def read_hotels(db: Session = Depends(get_db)):
    hotels = services.getAllHotels(db)
    return hotels

@router.get("/{hotel_id}", response_model=schemas.HotelsResponse)
def read_hotel(hotel_id: str, db: Session = Depends(get_db)):
    hotel = services.getHotelById(db, hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@router.get("/city/{city_id}", response_model=list[schemas.HotelsResponse])
def read_hotels_by_city(city_id: str, db: Session = Depends(get_db)):
    hotels = services.getHotelsByCityId(db, city_id)
    return hotels

@router.get("/nearby/", response_model=list[schemas.HotelsNearbyResponse])
def read_nearby_hotels(
    latitude: float,
    longitude: float,
    max_distance_km: float = 10.0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    hotels = services.getClosestHotels(db, latitude, longitude, max_distance_km, limit)
    return hotels

@router.post("/", response_model=schemas.HotelsResponse)
def create_hotel(hotel: schemas.HotelsCreate, db: Session = Depends(get_db)):
    return services.createHotel(db, hotel)

@router.put("/{hotel_id}", response_model=schemas.HotelsResponse)
def update_hotel(hotel_id: str, hotel: schemas.HotelsUpdate, db: Session = Depends(get_db)):
    updated_hotel = services.updateHotel(db, hotel_id, hotel)
    if updated_hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return updated_hotel

@router.delete("/{hotel_id}", response_model=dict)
def delete_hotel(hotel_id: str, db: Session = Depends(get_db)):
    success = services.deleteHotel(db, hotel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"detail": "Hotel deleted successfully"}
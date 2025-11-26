from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import database.schemas.hotels_schema as schemas
import database.schemas.hotel_details_schema as hotel_details_schemas
import services.hotels_service as services
import services.hotel_details_service as hotel_details_service
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

@router.get("/nearby/type/{hotel_type}", response_model=list[schemas.HotelsNearbyResponse])
def read_nearby_hotels_by_type(
    hotel_type: str,
    latitude: float,
    longitude: float,
    max_distance_km: float = 10.0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    hotels = services.getClosestHotelsByType(db, latitude, longitude, hotel_type, limit, max_distance_km)
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

@router.get("/unified/{hotel_id}", response_model=schemas.HotelsUnifiedResponse)
def get_unified_hotel_data(hotel_id: str, db: Session = Depends(get_db)):
    """Get unified hotel data including details for Mini App"""
    hotel = services.getHotelById(db, hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    # Get hotel details if available
    hotel_details = hotel_details_service.getHotelDetailsByHotelId(db, hotel_id)
    
    # Convert SQLAlchemy models to Pydantic models
    hotel_response = schemas.HotelsResponse.model_validate(hotel)
    details_response = None
    if hotel_details:
        details_response = hotel_details_schemas.HotelDetailsResponse.model_validate(hotel_details)
    
    # Create unified response
    unified_data = schemas.HotelsUnifiedResponse(
        hotel=hotel_response,
        details=details_response,
        maps_url=f"https://www.google.com/maps/search/?api=1&query={hotel.name}" if hotel.name else None,
        website_url=hotel.website if hotel.website else None,
        image_url=hotel.image_url if hotel.image_url else None
    )
    
    return unified_data

@router.delete("/{hotel_id}", response_model=dict)
def delete_hotel(hotel_id: str, db: Session = Depends(get_db)):
    success = services.deleteHotel(db, hotel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"detail": "Hotel deleted successfully"}
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import database.schemas.hotel_details_schema as schemas
import services.hotel_details_service as services
from database.engine_db import get_db

router = APIRouter(
    prefix="/hotel_details",
    tags=["Hotel Details"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.HotelDetailsResponse])
def get_hotel_details(db: Session = Depends(get_db)):
    hotel_details = services.getAllHotelDetails(db)
    return hotel_details

@router.get("/{hotel_id}", response_model=schemas.HotelDetailsResponse)
def get_hotel_detail_by_id(hotel_id: str, db: Session = Depends(get_db)):
    hotel_detail = services.getHotelDetailById(db, hotel_id)
    if hotel_detail is None:
        raise HTTPException(status_code=404, detail="Hotel detail not found")
    return hotel_detail

@router.post("/", response_model=schemas.HotelDetailsResponse)
def create_hotel_detail(hotel_detail: schemas.HotelDetailsCreate, db: Session = Depends(get_db)):
    return services.createHotelDetail(db, hotel_detail)

@router.put("/{hotel_id}", response_model=schemas.HotelDetailsResponse)
def update_hotel_detail(hotel_id: str, hotel_detail: schemas.HotelDetailsUpdate, db: Session = Depends(get_db)):
    updated_hotel_detail = services.updateHotelDetail(db, hotel_id, hotel_detail)
    if updated_hotel_detail is None:
        raise HTTPException(status_code=404, detail="Hotel detail not found")
    return updated_hotel_detail

@router.delete("/{hotel_id}", response_model=dict)
def delete_hotel_detail(hotel_id: str, db: Session = Depends(get_db)):
    success = services.deleteHotelDetail(db, hotel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hotel detail not found")
    return {"detail": "Hotel detail deleted successfully"}
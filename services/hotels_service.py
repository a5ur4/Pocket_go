from geoalchemy2 import Geography
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from models.hotels_model import HotelsModel
from models.evaluations_model import EvaluationsModel
import database.schemas.hotels_schema as schemas
from utils.logger import APILogger

def getAllHotels(db: Session):
    return db.query(HotelsModel).all()

def getHotelById(db: Session, hotel_id: str):
    return db.query(HotelsModel).filter(HotelsModel.id == hotel_id).first()

def getHotelsByCityId(db: Session, city_id: str):
    return db.query(HotelsModel).filter(HotelsModel.city_id == city_id).all()

def getPromotedHotels(db: Session):
    return db.query(HotelsModel).filter(HotelsModel.is_promoted == True).all()

def getClosestHotels(db: Session, latitude: float, longitude: float, limit: int = 10, max_distance_km: int = 20):
    """
    Finds the closest hotels to a given coordinate, along with their average ratings.

    Args:
        db (Session): The database session.
        latitude (float): The user's latitude.
        longitude (float): The user's longitude.
        limit (int): The maximum number of hotels to return.
        max_distance_km (int): The maximum search radius in kilometers.

    Returns:
        list: A list of tuples containing (Hotel, distance_in_km, average_rating).
    """

    # 1. Create a geographic point from the user's location
    # Order is important: longitude first, then latitude.
    user_location = func.ST_MakePoint(longitude, latitude).cast(Geography)

    # 2. Create a subquery to calculate the average rating for each hotel.
    # This avoids issues with hotels that have no ratings.
    # It will be left to use later.
    avg_rating_subquery = (
        select(

            EvaluationsModel.hotel_id,
            func.avg(EvaluationsModel.rating).label("avg_rating"),
            func.count(EvaluationsModel.id).label("review_count")
        )
        .group_by(EvaluationsModel.hotel_id)
        .subquery()
    )

    # 3. Calculate the distance from each hotel to the user
    distance_expression = func.ST_Distance(HotelsModel.location, user_location).label("distance_meters")

    # 4. Build the main query
    query = (
        db.query(
            HotelsModel,
            (distance_expression / 1000).label("distance_km"),
            # Use COALESCE to return 0.0 if there's no rating, instead of NULL
            func.coalesce(avg_rating_subquery.c.avg_rating, 0.0).label("avg_rating"),
            func.coalesce(avg_rating_subquery.c.review_count, 0).label("review_count")
        )
        # Use LEFT JOIN (outerjoin) to include hotels without ratings
        .outerjoin(
            avg_rating_subquery,
            HotelsModel.id == avg_rating_subquery.c.hotel_id,
        )
        # Filter only hotels within a maximum radius to optimize the search
        .filter(func.ST_DWithin(HotelsModel.location, user_location, max_distance_km * 1000))
        # Order by closest hotel
        .order_by(distance_expression.asc())
        # Limit the number of results
        .limit(limit)
    )

    # Execute the query and return the result
    results = query.all()
    
    # Log the search operation
    APILogger.log_hotel_search(
        latitude=latitude,
        longitude=longitude,
        results_count=len(results),
        search_type="nearby",
        max_distance_km=max_distance_km
    )
    
    # Format the results to match the HotelsNearbyResponse schema
    formatted_results = []
    for hotel_obj, distance_km, avg_rating, review_count in results:
        formatted_results.append({
            "hotel": hotel_obj,
            "distance_km": distance_km
        })
    
    return formatted_results

def getClosestHotelsByType(db: Session, latitude: float, longitude: float, hotel_type: str, limit: int = 10, max_distance_km: int = 20):
    """
    Finds the closest hotels of a specific type to a given coordinate.

    Args:
        db (Session): The database session.
        latitude (float): The user's latitude.
        longitude (float): The user's longitude.
        hotel_type (str): The type of hotel to filter by.
        limit (int): The maximum number of hotels to return.
        max_distance_km (int): The maximum search radius in kilometers.

    Returns:
        list: A list of dictionaries containing hotel and distance information.
    """
    
    # Create a geographic point from the user's location
    user_location = func.ST_MakePoint(longitude, latitude).cast(Geography)

    # Create a subquery for average ratings
    avg_rating_subquery = (
        select(
            EvaluationsModel.hotel_id,
            func.avg(EvaluationsModel.rating).label("avg_rating"),
            func.count(EvaluationsModel.id).label("review_count")
        )
        .group_by(EvaluationsModel.hotel_id)
        .subquery()
    )

    # Calculate distance expression
    distance_expression = func.ST_Distance(HotelsModel.location, user_location).label("distance_meters")

    # Build the main query with type filter
    query = (
        db.query(
            HotelsModel,
            (distance_expression / 1000).label("distance_km"),
            func.coalesce(avg_rating_subquery.c.avg_rating, 0.0).label("avg_rating"),
            func.coalesce(avg_rating_subquery.c.review_count, 0).label("review_count")
        )
        .outerjoin(
            avg_rating_subquery,
            HotelsModel.id == avg_rating_subquery.c.hotel_id,
        )
        # Filter by hotel type and distance
        .filter(HotelsModel.type == hotel_type)
        .filter(func.ST_DWithin(HotelsModel.location, user_location, max_distance_km * 1000))
        .order_by(distance_expression.asc())
        .limit(limit)
    )

    # Execute the query and format results
    results = query.all()
    
    # Log the search operation
    APILogger.log_hotel_search(
        latitude=latitude,
        longitude=longitude,
        results_count=len(results),
        search_type="nearby_by_type",
        hotel_type=hotel_type,
        max_distance_km=max_distance_km
    )
    
    formatted_results = []
    for hotel_obj, distance_km, avg_rating, review_count in results:
        formatted_results.append({
            "hotel": hotel_obj,
            "distance_km": distance_km
        })
    
    return formatted_results

def createHotel(db: Session, hotel: schemas.HotelsCreate):
    try:
        db_hotel = HotelsModel(
            name=hotel.name,
            description=hotel.description,
            type=hotel.type,
            address=hotel.address,
            city_id=hotel.city_id,
            location=hotel.location,
            web_evaluation_score=hotel.web_evaluation_score,
            image_url=hotel.image_url,
            phone=hotel.phone,
            email=hotel.email,
            website=hotel.website,
            is_promoted=hotel.is_promoted
        )
        db.add(db_hotel)
        db.commit()
        db.refresh(db_hotel)
        return db_hotel
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateHotel(db: Session, hotel_id: str, hotel: schemas.HotelsUpdate):
    try:
        db_hotel = db.query(HotelsModel).filter(HotelsModel.id == hotel_id).first()
        if not db_hotel:
            return None
        
        update_data = hotel.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_hotel, field, value)
        
        db.commit()
        db.refresh(db_hotel)
        return db_hotel
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteHotel(db: Session, hotel_id: str):
    try:
        db_hotel = db.query(HotelsModel).filter(HotelsModel.id == hotel_id).first()
        if not db_hotel:
            return False
        
        db.delete(db_hotel)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
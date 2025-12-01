from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.rate_plans_model import RatePlansModel
import database.schemas.rate_plans_schema as schemas

def getAllRatePlans(db: Session):
    return db.query(RatePlansModel).all()

def getRatePlanById(db: Session, rate_plan_id: str):
    return db.query(RatePlansModel).filter(RatePlansModel.id == rate_plan_id).first()

def getRatePlansByHotelId(db: Session, hotel_id: str):
    return db.query(RatePlansModel).filter(RatePlansModel.hotel_id == hotel_id).all()

def getRatePlansByName(db: Session, name: str):
    return db.query(RatePlansModel).filter(RatePlansModel.name == name).all()

def createRatePlan(db: Session, rate_plan: schemas.RatePlansCreate):
    try:
        db_rate_plan = RatePlansModel(
            hotel_id=rate_plan.hotel_id,
            name=rate_plan.name,
            billing_cycle=rate_plan.billing_cycle,
            duration_minutes=rate_plan.duration_minutes
        )
        db.add(db_rate_plan)
        db.commit()
        db.refresh(db_rate_plan)
        return db_rate_plan
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateRatePlan(db: Session, rate_plan_id: str, rate_plan: schemas.RatePlansUpdate):
    try:
        db_rate_plan = db.query(RatePlansModel).filter(RatePlansModel.id == rate_plan_id).first()
        if not db_rate_plan:
            return None
        
        update_data = rate_plan.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rate_plan, field, value)
        
        db.commit()
        db.refresh(db_rate_plan)
        return db_rate_plan
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteRatePlan(db: Session, rate_plan_id: str):
    try:
        db_rate_plan = db.query(RatePlansModel).filter(RatePlansModel.id == rate_plan_id).first()
        if not db_rate_plan:
            return False
        
        db.delete(db_rate_plan)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
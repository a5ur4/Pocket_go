from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from models.evaluations_model import EvaluationsModel
import database.schemas.evaluations_schema as schemas

def getAllEvaluations(db: Session):
    return db.query(EvaluationsModel).all()

def getEvaluationById(db: Session, evaluation_id: str):
    return db.query(EvaluationsModel).filter(EvaluationsModel.id == evaluation_id).first()

def getEvaluationsByHotelId(db: Session, hotel_id: str):
    return db.query(EvaluationsModel).filter(EvaluationsModel.hotel_id == hotel_id).all()

def getAverageRatingByHotelId(db: Session, hotel_id: str):
    result = db.query(func.avg(EvaluationsModel.rating)).filter(EvaluationsModel.hotel_id == hotel_id).scalar()
    return result

def createEvaluation(db: Session, evaluation: schemas.EvaluationsCreate):
    try:
        db_evaluation = EvaluationsModel(
            hotel_id=evaluation.hotel_id,
            rating=evaluation.rating,
            comment=evaluation.comment,
            author_identifier=evaluation.author_identifier
        )
        db.add(db_evaluation)
        db.commit()
        db.refresh(db_evaluation)
        return db_evaluation
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def updateEvaluation(db: Session, evaluation_id: str, evaluation: schemas.EvaluationsUpdate):
    try:
        db_evaluation = db.query(EvaluationsModel).filter(EvaluationsModel.id == evaluation_id).first()
        if not db_evaluation:
            return None
        
        update_data = evaluation.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_evaluation, field, value)
        
        db.commit()
        db.refresh(db_evaluation)
        return db_evaluation
    except SQLAlchemyError as e:
        db.rollback()
        raise e

def deleteEvaluation(db: Session, evaluation_id: str):
    try:
        db_evaluation = db.query(EvaluationsModel).filter(EvaluationsModel.id == evaluation_id).first()
        if not db_evaluation:
            return False
        
        db.delete(db_evaluation)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e
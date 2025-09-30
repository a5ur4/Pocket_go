from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import database.schemas.evaluations_schema as schemas
import services.evaluations_service as services
from database.engine_db import get_db

router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.EvaluationsResponse])
def read_evaluations(db: Session = Depends(get_db)):
    evaluations = services.getAllEvaluations(db)
    return evaluations

@router.get("/{evaluation_id}", response_model=schemas.EvaluationsResponse)
def read_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = services.getEvaluationById(db, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation

@router.get("/hotel/{hotel_id}", response_model=list[schemas.EvaluationsResponse])
def read_evaluation_by_hotel(hotel_id: str, db: Session = Depends(get_db)):
    evaluations = services.getEvaluationsByHotelId(db, hotel_id)
    return evaluations

@router.get("/hotel/{hotel_id}/average-rating", response_model=float)
def read_average_rating(hotel_id: str, db: Session = Depends(get_db)):
    average_rating = services.getAverageRatingByHotelId(db, hotel_id)
    return average_rating if average_rating is not None else 0.0

@router.post("/", response_model=schemas.EvaluationsResponse)
def create_evaluation(evaluation: schemas.EvaluationsCreate, db: Session = Depends(get_db)):
    return services.createEvaluation(db, evaluation)

@router.put("/{evaluation_id}", response_model=schemas.EvaluationsResponse)
def update_evaluation(evaluation_id: str, evaluation: schemas.EvaluationsUpdate, db: Session = Depends(get_db)):
    updated_evaluation = services.updateEvaluation(db, evaluation_id, evaluation)
    if updated_evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return updated_evaluation

@router.delete("/{evaluation_id}", response_model=dict)
def delete_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    success = services.deleteEvaluation(db, evaluation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return {"detail": "Evaluation deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.engine_db import get_db
from services import rate_plans_service
from database.schemas.rate_plans_schema import (
    RatePlansCreate, RatePlansUpdate, RatePlansResponse
)

router = APIRouter(prefix="/rate-plans", tags=["Rate Plans"])

@router.get("/", response_model=List[RatePlansResponse])
async def get_all_rate_plans(db: Session = Depends(get_db)):
    """Listar todos os planos de tarifas"""
    rate_plans = rate_plans_service.getAllRatePlans(db)
    return rate_plans

@router.get("/{rate_plan_id}", response_model=RatePlansResponse)
async def get_rate_plan_by_id(rate_plan_id: UUID, db: Session = Depends(get_db)):
    """Obter plano de tarifa por ID"""
    rate_plan = rate_plans_service.getRatePlanById(db, str(rate_plan_id))
    if not rate_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano de tarifa não encontrado"
        )
    return rate_plan

@router.get("/hotel/{hotel_id}", response_model=List[RatePlansResponse])
async def get_rate_plans_by_hotel_id(hotel_id: UUID, db: Session = Depends(get_db)):
    """Listar planos de tarifa de um hotel específico"""
    rate_plans = rate_plans_service.getRatePlansByHotelId(db, str(hotel_id))
    return rate_plans

@router.get("/search/", response_model=List[RatePlansResponse])
async def get_rate_plans_by_name(name: str, db: Session = Depends(get_db)):
    """Buscar planos de tarifa por nome"""
    rate_plans = rate_plans_service.getRatePlansByName(db, name)
    return rate_plans

@router.post("/", response_model=RatePlansResponse, status_code=status.HTTP_201_CREATED)
async def create_rate_plan(rate_plan: RatePlansCreate, db: Session = Depends(get_db)):
    """Criar novo plano de tarifa"""
    try:
        return rate_plans_service.createRatePlan(db, rate_plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar plano de tarifa: {str(e)}"
        )

@router.put("/{rate_plan_id}", response_model=RatePlansResponse)
async def update_rate_plan(
    rate_plan_id: UUID,
    rate_plan: RatePlansUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar plano de tarifa"""
    try:
        updated_rate_plan = rate_plans_service.updateRatePlan(db, str(rate_plan_id), rate_plan)
        if not updated_rate_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plano de tarifa não encontrado"
            )
        return updated_rate_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar plano de tarifa: {str(e)}"
        )

@router.delete("/{rate_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rate_plan(rate_plan_id: UUID, db: Session = Depends(get_db)):
    """Excluir plano de tarifa"""
    try:
        success = rate_plans_service.deleteRatePlan(db, str(rate_plan_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plano de tarifa não encontrado"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao excluir plano de tarifa: {str(e)}"
        )
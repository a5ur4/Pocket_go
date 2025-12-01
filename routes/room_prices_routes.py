from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.engine_db import get_db
from services import room_prices_service
from database.schemas.room_prices_schema import (
    RoomPricesCreate, RoomPricesUpdate, RoomPricesResponse, RoomPricesWithDetailsResponse
)

router = APIRouter(prefix="/room-prices", tags=["Room Prices"])

@router.get("/", response_model=List[RoomPricesResponse])
async def get_all_room_prices(db: Session = Depends(get_db)):
    """Listar todos os preços de quartos"""
    room_prices = room_prices_service.getAllRoomPrices(db)
    return room_prices

@router.get("/{room_price_id}", response_model=RoomPricesResponse)
async def get_room_price_by_id(room_price_id: UUID, db: Session = Depends(get_db)):
    """Obter preço de quarto por ID"""
    room_price = room_prices_service.getRoomPriceById(db, str(room_price_id))
    if not room_price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preço de quarto não encontrado"
        )
    return room_price

@router.get("/room-type/{room_type_id}", response_model=List[RoomPricesResponse])
async def get_room_prices_by_room_type_id(room_type_id: UUID, db: Session = Depends(get_db)):
    """Listar preços por tipo de quarto"""
    room_prices = room_prices_service.getRoomPricesByRoomTypeId(db, str(room_type_id))
    return room_prices

@router.get("/rate-plan/{rate_plan_id}", response_model=List[RoomPricesResponse])
async def get_room_prices_by_rate_plan_id(rate_plan_id: UUID, db: Session = Depends(get_db)):
    """Listar preços por plano de tarifa"""
    room_prices = room_prices_service.getRoomPricesByRatePlanId(db, str(rate_plan_id))
    return room_prices

@router.get("/search/price-range/", response_model=List[RoomPricesResponse])
async def get_room_prices_by_price_range(
    min_price: float,
    max_price: float,
    db: Session = Depends(get_db)
):
    """Buscar preços dentro de uma faixa específica"""
    if min_price < 0 or max_price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preços não podem ser negativos"
        )
    if min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preço mínimo não pode ser maior que o máximo"
        )
    
    room_prices = room_prices_service.getByPriceRange(db, min_price, max_price)
    return room_prices

@router.post("/", response_model=RoomPricesResponse, status_code=status.HTTP_201_CREATED)
async def create_room_price(room_price: RoomPricesCreate, db: Session = Depends(get_db)):
    """Criar novo preço de quarto"""
    try:
        return room_prices_service.createRoomPrice(db, room_price)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar preço de quarto: {str(e)}"
        )

@router.put("/{room_price_id}", response_model=RoomPricesResponse)
async def update_room_price(
    room_price_id: UUID,
    room_price: RoomPricesUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar preço de quarto"""
    try:
        updated_room_price = room_prices_service.updateRoomPrice(db, str(room_price_id), room_price)
        if not updated_room_price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preço de quarto não encontrado"
            )
        return updated_room_price
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar preço de quarto: {str(e)}"
        )

@router.delete("/{room_price_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_price(room_price_id: UUID, db: Session = Depends(get_db)):
    """Excluir preço de quarto"""
    try:
        success = room_prices_service.deleteRoomPrice(db, str(room_price_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preço de quarto não encontrado"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao excluir preço de quarto: {str(e)}"
        )
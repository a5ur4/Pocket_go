from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.engine_db import get_db
from services import room_types_service
from database.schemas.room_types_schema import (
    RoomTypesCreate, RoomTypesUpdate, RoomTypesResponse, RoomTypesWithHotelResponse
)

router = APIRouter(prefix="/room-types", tags=["Room Types"])

@router.get("/", response_model=List[RoomTypesResponse])
async def get_all_room_types(db: Session = Depends(get_db)):
    """Listar todos os tipos de quarto"""
    room_types = room_types_service.getAllRoomTypes(db)
    return room_types

@router.get("/{room_type_id}", response_model=RoomTypesResponse)
async def get_room_type_by_id(room_type_id: UUID, db: Session = Depends(get_db)):
    """Obter tipo de quarto por ID"""
    room_type = room_types_service.getRoomTypeById(db, str(room_type_id))
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de quarto não encontrado"
        )
    return room_type

@router.get("/hotel/{hotel_id}", response_model=List[RoomTypesResponse])
async def get_room_types_by_hotel_id(hotel_id: UUID, db: Session = Depends(get_db)):
    """Listar tipos de quarto de um hotel específico"""
    room_types = room_types_service.getRoomTypesByHotelId(db, str(hotel_id))
    return room_types

@router.post("/", response_model=RoomTypesResponse, status_code=status.HTTP_201_CREATED)
async def create_room_type(room_type: RoomTypesCreate, db: Session = Depends(get_db)):
    """Criar novo tipo de quarto"""
    try:
        return room_types_service.createRoomType(db, room_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar tipo de quarto: {str(e)}"
        )

@router.put("/{room_type_id}", response_model=RoomTypesResponse)
async def update_room_type(
    room_type_id: UUID,
    room_type: RoomTypesUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar tipo de quarto"""
    try:
        updated_room_type = room_types_service.updateRoomType(db, str(room_type_id), room_type)
        if not updated_room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de quarto não encontrado"
            )
        return updated_room_type
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar tipo de quarto: {str(e)}"
        )

@router.delete("/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_type(room_type_id: UUID, db: Session = Depends(get_db)):
    """Excluir tipo de quarto"""
    try:
        success = room_types_service.deleteRoomType(db, str(room_type_id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de quarto não encontrado"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao excluir tipo de quarto: {str(e)}"
        )
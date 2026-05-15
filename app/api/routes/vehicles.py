from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate
from app.repositories import vehicle_repository as vehicle_repo
from app.repositories import client_repository as client_repo


router = APIRouter(
    prefix="/clients/{cpf}/vehicles",
    tags=["Vehicles"],
    dependencies=[Depends(get_current_user)],
    
)

@router.get("/", response_model=list[VehicleResponse])
def list_vehicles(cpf: str, db: Session = Depends(get_db)):
    client = client_repo.get_by_cpf(db, cpf)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return vehicle_repo.get_all_by_client(db, client.id)


@router.post("/", response_model=VehicleResponse, status_code=201)
def create_vehicle(
    cpf: str,
    data: VehicleCreate,
    db: Session = Depends(get_db),
):
    client = client_repo.get_by_cpf(db, cpf)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if vehicle_repo.get_by_plate(db, data.plate):
        raise HTTPException(
            status_code=400,
            detail="Vehicle with this plate already exists",
        )

    return vehicle_repo.create(db, client.id, data)

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    cpf: str,
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
):
    # 1. Validar cliente
    client = client_repo.get_by_cpf(db, cpf)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 2. Buscar veículo
    vehicle = vehicle_repo.get_by_id(db, vehicle_id)
    if not vehicle or vehicle.client_id != client.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # 3. Validar placa duplicada (se estiver sendo alterada)
    if data.plate:
        existing = vehicle_repo.get_by_plate(db, data.plate)
        if existing and existing.id != vehicle.id:
            raise HTTPException(
                status_code=400,
                detail="Vehicle with this plate already exists",
            )

    # 4. Atualizar
    return vehicle_repo.update(db, vehicle, data)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    cpf: str,
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    client = client_repo.get_by_cpf(db, cpf)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    vehicle = vehicle_repo.get_by_id(db, vehicle_id)
    if not vehicle or vehicle.client_id != client.id:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle_repo.delete(db, vehicle)

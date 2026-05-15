from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleUpdate

def get_all_by_client(db: Session, client_id: int):
    return db.query(Vehicle).filter(Vehicle.client_id == client_id).all()

def get_by_id(db: Session, vehicle_id: int):
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def get_by_plate(db: Session, plate: str):
    return db.query(Vehicle).filter(Vehicle.plate == plate).first()

def create(db: Session, client_id: int, data):
    vehicle = Vehicle(client_id=client_id, **data.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

def update(db, vehicle, data: VehicleUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle

def delete(db: Session, vehicle: Vehicle):
    db.delete(vehicle)
    db.commit()

from sqlalchemy.orm import Session
from app.models.part import Part
from app.schemas.part import PartCreate, PartUpdate


def get_all(db: Session):
    return db.query(Part).all()


def get_by_id(db: Session, part_id: int):
    return db.query(Part).filter(Part.id == part_id).first()


def get_by_name(db: Session, name: str):
    return db.query(Part).filter(Part.name == name).first()


def create(db: Session, data: PartCreate):
    part = Part(**data.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


def update(db: Session, part: Part, data: PartUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(part, field, value)

    db.commit()
    db.refresh(part)
    return part


def delete(db: Session, part: Part):
    db.delete(part)
    db.commit()

from app.repositories import stock_movement_repository as repo
from app.models.part import Part
from app.schemas.stock_movement import StockMovementCreate

def test_create_stock_in_movement(db_session):
    part = Part(name="Filtro de Óleo", price=50.0, quantity=10, unit="1")
    db_session.add(part)
    db_session.commit()
    
    data = StockMovementCreate(movement_type="IN", quantity=5, reference="Compra")
    updated_part = repo.create_movement(db_session, part, data, new_quantity=15)
    
    assert updated_part.quantity == 15
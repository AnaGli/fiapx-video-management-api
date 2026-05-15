from decimal import Decimal

from app.models.service_order import ServiceOrder
from app.models.service_order_item import ServiceOrderItem
from app.repositories.service_order_repository import recalculate_total


def test_recalculate_total_updates_order_amount(db_session):
    # arrange
    order = ServiceOrder(
        client_id=1,
        vehicle_id=1,
        status="RECEBIDA",
        total_amount=0,
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    item1 = ServiceOrderItem(
        service_order_id=order.id,
        item_type="SERVICE",
        item_id=1,
        description="Troca de óleo",
        quantity=2,
        price=Decimal("100.00"),
    )

    item2 = ServiceOrderItem(
        service_order_id=order.id,
        item_type="PART",
        item_id=2,
        description="Óleo 5W30",
        quantity=3,
        price=Decimal("50.00"),
    )

    db_session.add_all([item1, item2])
    db_session.commit()
    db_session.refresh(order)

    # act
    recalculate_total(db_session, order)

    # assert
    db_session.refresh(order)
    assert order.total_amount == Decimal("350.00")

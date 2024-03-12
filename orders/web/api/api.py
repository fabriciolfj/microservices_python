from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from flask import Response
from starlette import status

from orders.orders_service.exceptions import OrderNotFoundError
from orders.orders_service.orders_service import OrdersService
from orders.repository.UnitOfWork import UnitOfWork
from orders.repository.orders_repository import OrdersRepository
from orders.web.api.schemas import (GetOrderSchema, CreateOrderSchema, GetOrdersSchema)
from orders.web.app import app


@app.get("/orders", response_model=GetOrdersSchema)
def get_orders(cancelled: Optional[bool] = None, limit: Optional[int] = None):
    with UnitOfWork() as unit_to_work:
        repo = OrdersRepository(unit_to_work.session)
        orders_service = OrdersService(repo)
        results = orders_service.list_orders(cancelled=cancelled, limit=limit)

        return {'orders': [result.dict() for result in results]}



@app.post('/orders', status_code=status.HTTP_201_CREATED, response_model=GetOrderSchema)
def create_order(payload: CreateOrderSchema):
    print(f'payload {payload}')
    with UnitOfWork() as unit_of_work:
        repo = OrdersRepository(unit_of_work.session)
        order_service = OrdersService(repo)
        order = payload.dict()['order']
        print(f'order payload {order}')
        for item in order:
            item['size'] = item['size'].value
        order = order_service.place_order(order)

        unit_of_work.commit()
        return_payload = order.dict()
    return return_payload


@app.get('/orders/{order_id}', response_model=GetOrderSchema)
def get_order(order_id: UUID):
    try:
        with UnitOfWork() as unit_to_work:
            repo = OrdersRepository(unit_to_work.session)
            service = OrdersService(repo)
            order = service.get_order(order_id)
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail=f'Order with ID {order_id} not found')


@app.put('/orders/{order_id}', response_model=GetOrderSchema)
def update_order(order_id: UUID, order_details: CreateOrderSchema):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = order_details.dict()['order']
            for item in order:
                item['size'] = item['size'].value
            order = orders_service.update_order(
                order_id=order_id, items=order
            )
            unit_of_work.commit()
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Order with ID {order_id} not found'
        )


@app.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_order(order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            orders_service.delete_order(order_id=order_id)
            unit_of_work.commit()
        return
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Order with ID {order_id} not found'
        )


@app.post('/orders/{order_id}/cancel', response_model=GetOrderSchema)
def cancel_order(order_id: UUID):
    try:
        with UnitOfWork as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            service = OrdersService(repo)
            order = service.cancel_order(order_id)
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Order with ID {order_id} not found'
        )


@app.post('/orders/{order_id}/pay', response_model=GetOrderSchema)
def pay_order(order_id: UUID):
    try:
        with UnitOfWork() as unit_of_work:
            repo = OrdersRepository(unit_of_work.session)
            orders_service = OrdersService(repo)
            order = orders_service.pay_order(order_id=order_id)
            unit_of_work.commit()
        return order.dict()
    except OrderNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Order with ID {order_id} not found'
        )

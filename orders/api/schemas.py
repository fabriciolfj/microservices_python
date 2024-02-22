from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, conlist, conint
from pydantic.v1 import validator


class Size(Enum):
    small = 'small'
    medium = 'medium'
    big = 'big'


class Status(Enum):
    created = 'created'
    progress = 'progress'
    cancelled = 'cancelled'
    dispatched = 'dispatched'
    delivered = 'delivered'


class OrderItemSchema(BaseModel):
    product: str
    size: Size
    quantity: Optional[conint(ge=1, strict=True)] = 1

    @validator('quantity')
    def quantity_non_nullable(self, value):
        assert value is not None, 'quantity may not be None'
        return value


class CreateOrderSchema(BaseModel):
    order: conlist(OrderItemSchema)


class GetOrderSchema(CreateOrderSchema):
    id: UUID
    created: datetime
    status: Status


class GetOrdersSchema(BaseModel):
    orders: List[GetOrderSchema]

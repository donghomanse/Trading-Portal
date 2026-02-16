from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models import TradeType, TradeStatus

# Base schema
class TradeBase(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    trade_type: TradeType = Field(..., description="Trade type: buy or sell")
    quantity: int = Field(..., gt=0, description="Number of shares")
    price: float = Field(..., gt=0, description="Price per share")

# Schema for creating a trade
class TradeCreate(TradeBase):
    pass

# Schema for updating a trade
class TradeUpdate(BaseModel):
    status: Optional[TradeStatus] = None
    quantity: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)

# Schema for reading a trade (response)
class TradeResponse(TradeBase):
    id: int
    status: TradeStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

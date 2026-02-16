from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class TradeType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)  # e.g., "AAPL", "GOOGL"
    trade_type = Column(Enum(TradeType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, type={self.trade_type}, quantity={self.quantity})>"

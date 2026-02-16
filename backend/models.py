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


class Stock(Base):
    __tablename__ = "stocks"

    code = Column(String(10), primary_key=True, index=True)  # 단축코드
    standard_code = Column(String(20))  # 표준코드
    name = Column(String(100), nullable=False, index=True)  # 한글명
    market = Column(String(20))  # 시장구분 (KOSPI/KOSDAQ)

    # 가격 정보
    base_price = Column(Integer)  # 기준가
    market_cap = Column(Float)  # 시가총액

    # 상장 정보
    listing_date = Column(String(10))  # 상장일자
    listing_shares = Column(Float)  # 상장주수
    capital = Column(Float)  # 자본금
    par_value = Column(Float)  # 액면가

    # 재무 정보
    revenue = Column(Float)  # 매출액
    operating_profit = Column(Float)  # 영업이익
    net_profit = Column(Float)  # 당기순이익
    roe = Column(Float)  # ROE
    fiscal_month = Column(String(2))  # 결산월

    # KRX 분류
    krx = Column(String(1))  # KRX
    krx_semiconductor = Column(String(1))  # KRX반도체
    krx_bio = Column(String(1))  # KRX바이오
    krx_banking = Column(String(1))  # KRX은행
    krx_auto = Column(String(1))  # KRX자동차
    krx300 = Column(String(1))  # KRX300
    kospi = Column(String(1))  # KOSPI

    # 거래 정보
    margin_rate = Column(Integer)  # 증거금비율
    credit_available = Column(String(1))  # 신용가능
    suspended = Column(String(1))  # 거래정지
    administered = Column(String(1))  # 관리종목

    # 메타 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Stock(code={self.code}, name={self.name}, price={self.base_price})>"

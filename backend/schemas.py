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


class StockPriceResponse(BaseModel):
    """주식 현재가 시세2 응답 (v1_국내주식-054)"""

    # 기본 가격 정보
    stck_prpr: int              # 현재가
    prdy_vrss: int              # 전일 대비
    prdy_vrss_sign: str         # 전일 대비 부호 (1:상한 2:상승 3:보합 4:하한 5:하락)
    prdy_ctrt: float            # 전일 대비율 (%)
    stck_prdy_clpr: int         # 전일 종가

    # 거래 정보
    acml_vol: int               # 누적 거래량
    acml_tr_pbmn: int           # 누적 거래대금
    prdy_vrss_vol_rate: Optional[float] = None  # 전일 대비 거래량 비율
    prdy_vol: int = 0           # 전일 거래량

    # 가격 범위
    stck_oprc: int              # 시가
    stck_hgpr: int              # 최고가
    stck_lwpr: int              # 최저가
    stck_mxpr: int              # 상한가
    stck_llam: int              # 하한가
    stck_sdpr: int              # 기준가

    # 시가 대비
    oprc_vrss_prpr: int = 0             # 시가 대비 현재가
    oprc_vrss_prpr_sign: str = "3"      # 시가 대비 부호
    prdy_clpr_vrss_oprc_rate: Optional[float] = None  # 전일 종가 대비 시가 비율

    # 고가 대비
    hgpr_vrss_prpr: int = 0             # 최고가 대비 현재가
    hgpr_vrss_prpr_sign: str = "3"      # 최고가 대비 부호
    prdy_clpr_vrss_hgpr_rate: Optional[float] = None  # 전일 종가 대비 최고가 비율

    # 저가 대비
    lwpr_vrss_prpr: int = 0             # 최저가 대비 현재가
    lwpr_vrss_prpr_sign: str = "3"      # 최저가 대비 부호
    prdy_clpr_vrss_lwpr_rate: Optional[float] = None  # 전일 종가 대비 최저가 비율

    # 종목 상태
    bstp_kor_isnm: str = ""             # 업종 한글 종목명
    rprs_mrkt_kor_name: str = ""        # 대표 시장 한글 명
    marg_rate: Optional[float] = None   # 증거금 비율
    crdt_rate: Optional[float] = None   # 신용 비율
    crdt_able_yn: str = ""              # 신용 가능 여부
    trht_yn: str = "N"                  # 거래정지 여부
    mang_issu_yn: str = "N"             # 관리 종목 여부
    sltr_yn: str = "N"                  # 정리매매 여부
    invt_caful_yn: str = "N"            # 투자주의여부
    mrkt_warn_cls_code: str = "00"      # 시장경고코드
    short_over_yn: str = "N"            # 단기과열여부

    @classmethod
    def from_kis_output(cls, output: dict) -> "StockPriceResponse":
        """KIS API output dict를 파싱하여 응답 객체 생성"""

        def to_int(v):
            try:
                return int(v)
            except (ValueError, TypeError):
                return 0

        def to_float(v):
            try:
                return float(v)
            except (ValueError, TypeError):
                return None

        return cls(
            stck_prpr=to_int(output.get("stck_prpr")),
            prdy_vrss=to_int(output.get("prdy_vrss")),
            prdy_vrss_sign=output.get("prdy_vrss_sign", "3"),
            prdy_ctrt=float(output.get("prdy_ctrt", "0")),
            stck_prdy_clpr=to_int(output.get("stck_prdy_clpr")),
            acml_vol=to_int(output.get("acml_vol")),
            acml_tr_pbmn=to_int(output.get("acml_tr_pbmn")),
            prdy_vrss_vol_rate=to_float(output.get("prdy_vrss_vol_rate")),
            prdy_vol=to_int(output.get("prdy_vol")),
            stck_oprc=to_int(output.get("stck_oprc")),
            stck_hgpr=to_int(output.get("stck_hgpr")),
            stck_lwpr=to_int(output.get("stck_lwpr")),
            stck_mxpr=to_int(output.get("stck_mxpr")),
            stck_llam=to_int(output.get("stck_llam")),
            stck_sdpr=to_int(output.get("stck_sdpr")),
            oprc_vrss_prpr=to_int(output.get("oprc_vrss_prpr")),
            oprc_vrss_prpr_sign=output.get("oprc_vrss_prpr_sign", "3"),
            prdy_clpr_vrss_oprc_rate=to_float(output.get("prdy_clpr_vrss_oprc_rate")),
            hgpr_vrss_prpr=to_int(output.get("hgpr_vrss_prpr")),
            hgpr_vrss_prpr_sign=output.get("hgpr_vrss_prpr_sign", "3"),
            prdy_clpr_vrss_hgpr_rate=to_float(output.get("prdy_clpr_vrss_hgpr_rate")),
            lwpr_vrss_prpr=to_int(output.get("lwpr_vrss_prpr")),
            lwpr_vrss_prpr_sign=output.get("lwpr_vrss_prpr_sign", "3"),
            prdy_clpr_vrss_lwpr_rate=to_float(output.get("prdy_clpr_vrss_lwpr_rate")),
            bstp_kor_isnm=output.get("bstp_kor_isnm", "").strip(),
            rprs_mrkt_kor_name=output.get("rprs_mrkt_kor_name", "").strip(),
            marg_rate=to_float(output.get("marg_rate")),
            crdt_rate=to_float(output.get("crdt_rate")),
            crdt_able_yn=output.get("crdt_able_yn", ""),
            trht_yn=output.get("trht_yn", "N"),
            mang_issu_yn=output.get("mang_issu_yn", "N"),
            sltr_yn=output.get("sltr_yn", "N"),
            invt_caful_yn=output.get("invt_caful_yn", "N"),
            mrkt_warn_cls_code=output.get("mrkt_warn_cls_code", "00"),
            short_over_yn=output.get("short_over_yn", "N"),
        )

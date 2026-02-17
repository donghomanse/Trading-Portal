"""한국투자증권 Open API 클라이언트

OAuth 토큰 관리 및 주식 시세 조회 기능을 제공합니다.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

KIS_APP_KEY = os.getenv("KIS_APP_KEY")
KIS_APP_SECRET = os.getenv("KIS_APP_SECRET")
KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"

# 파일 로거 설정
_log_dir = Path(__file__).parent / "logs"
_log_dir.mkdir(exist_ok=True)

_logger = logging.getLogger("kis_api")
_logger.setLevel(logging.DEBUG)
_handler = logging.FileHandler(_log_dir / "kis_api.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
_logger.addHandler(_handler)

# 메모리 캐시된 토큰 상태
_access_token: str | None = None
_token_expires_at: datetime | None = None


class KISAPIError(Exception):
    """KIS API 오류"""

    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


async def _fetch_token() -> str:
    """OAuth 토큰 발급"""
    global _access_token, _token_expires_at

    req_body = {
        "grant_type": "client_credentials",
        "appkey": KIS_APP_KEY,
        "appsecret": "***MASKED***",
    }
    _logger.info(f"[토큰 요청] POST {KIS_BASE_URL}/oauth2/tokenP | body: {json.dumps(req_body, ensure_ascii=False)}")

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            f"{KIS_BASE_URL}/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": KIS_APP_KEY,
                "appsecret": KIS_APP_SECRET,
            },
        )
        data = response.json()

        # 응답 로깅 (토큰 값은 앞 20자만)
        log_data = {k: v for k, v in data.items()}
        if "access_token" in log_data:
            log_data["access_token"] = log_data["access_token"][:20] + "..."
        _logger.info(f"[토큰 응답] status={response.status_code} | body: {json.dumps(log_data, ensure_ascii=False)}")

        if response.status_code != 200:
            error_msg = data.get("error_description", response.text)
            _logger.error(f"[토큰 오류] {error_msg}")
            raise KISAPIError(
                message=f"토큰 발급 실패: {error_msg}",
                error_code=data.get("error_code"),
            )

        _access_token = data["access_token"]

        expires_str = data.get("access_token_token_expired", "")
        if expires_str:
            _token_expires_at = datetime.strptime(expires_str, "%Y-%m-%d %H:%M:%S")
        else:
            _token_expires_at = datetime.now() + timedelta(hours=23, minutes=50)

        print(f"[KIS] 토큰 발급 완료, 만료: {_token_expires_at}")
        return _access_token


async def get_access_token() -> str:
    """캐시된 토큰 반환, 만료 시 자동 갱신"""
    global _access_token, _token_expires_at

    if (
        _access_token
        and _token_expires_at
        and datetime.now() < _token_expires_at - timedelta(minutes=1)
    ):
        return _access_token

    return await _fetch_token()


async def get_stock_price(stock_code: str, _retry: bool = True) -> dict:
    """주식현재가 시세2 조회 (v1_국내주식-054)

    Args:
        stock_code: 종목코드 (예: 005930)
        _retry: 토큰 만료 시 재시도 여부 (내부용)

    Returns:
        KIS API output dict
    """
    global _access_token

    token = await get_access_token()

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": KIS_APP_KEY,
        "appsecret": KIS_APP_SECRET,
        "tr_id": "FHPST01010000",
        "custtype": "P",
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
    }

    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price-2"
    _logger.info(f"[시세 요청] GET {url} | params: {json.dumps(params)} | tr_id: FHPST01010000")

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        _logger.info(
            f"[시세 응답] stock={stock_code} | status={response.status_code} "
            f"| rt_cd={data.get('rt_cd')} | msg={data.get('msg1')} "
            f"| output: {json.dumps(data.get('output', {}), ensure_ascii=False)}"
        )

        if data.get("rt_cd") != "0":
            _logger.error(f"[시세 오류] stock={stock_code} | msg_cd={data.get('msg_cd')} | msg1={data.get('msg1')}")
            if data.get("msg_cd") == "EGW00123" and _retry:
                _access_token = None
                return await get_stock_price(stock_code, _retry=False)
            raise KISAPIError(
                message=data.get("msg1", "Unknown KIS API error"),
                error_code=data.get("msg_cd"),
            )

        return data.get("output", {})

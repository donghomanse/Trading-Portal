import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import './StockRealTime.css'

function StockRealTime() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [stock, setStock] = useState(null)
  const [price, setPrice] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [code])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [stockRes, priceRes] = await Promise.all([
        fetch(`/api/stocks/${code}`),
        fetch(`/api/stocks/${code}/price`),
      ])

      if (!stockRes.ok) {
        throw new Error(stockRes.status === 404 ? '종목을 찾을 수 없습니다' : '종목 정보 로딩 실패')
      }
      if (!priceRes.ok) {
        throw new Error('실시간 시세 조회에 실패했습니다')
      }

      const [stockData, priceData] = await Promise.all([
        stockRes.json(),
        priceRes.json(),
      ])

      setStock(stockData)
      setPrice(priceData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (value) => {
    if (value === null || value === undefined) return '-'
    return new Intl.NumberFormat('ko-KR').format(value)
  }

  const formatAmount = (value) => {
    if (value === null || value === undefined) return '-'
    const eok = Math.floor(value / 100000000)
    if (eok > 0) return `${formatNumber(eok)}억`
    const man = Math.floor(value / 10000)
    return `${formatNumber(man)}만`
  }

  const getSign = (sign) => {
    switch (sign) {
      case '1': return { symbol: '▲', cls: 'up-limit' }
      case '2': return { symbol: '▲', cls: 'up' }
      case '4': return { symbol: '▼', cls: 'down-limit' }
      case '5': return { symbol: '▼', cls: 'down' }
      default:  return { symbol: '-', cls: 'flat' }
    }
  }

  if (loading) {
    return (
      <div className="realtime-container">
        <div className="loading">실시간 시세를 불러오는 중...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="realtime-container">
        <div className="error-container">
          <div className="error-message">{error}</div>
          <button className="back-button" onClick={() => navigate('/stocks')}>
            ← 목록으로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  if (!price || !stock) return null

  const sign = getSign(price.prdy_vrss_sign)
  const oprcSign = getSign(price.oprc_vrss_prpr_sign)
  const hgprSign = getSign(price.hgpr_vrss_prpr_sign)
  const lwprSign = getSign(price.lwpr_vrss_prpr_sign)

  return (
    <div className="realtime-container">
      <div className="realtime-header">
        <button className="back-button" onClick={() => navigate('/stocks')}>
          ← 목록으로
        </button>
        <div className="realtime-title">
          <h1>{stock.name}</h1>
          <span className="realtime-code-badge">{stock.code}</span>
          <span className="realtime-badge">REAL TIME</span>
        </div>
        {price.bstp_kor_isnm && (
          <div className="realtime-subtitle">{price.rprs_mrkt_kor_name} / {price.bstp_kor_isnm}</div>
        )}
      </div>

      <div className="price-hero">
        <div className="current-price">{formatNumber(price.stck_prpr)}원</div>
        <div className={`price-change ${sign.cls}`}>
          {sign.symbol} {formatNumber(Math.abs(price.prdy_vrss))}원
          ({price.prdy_ctrt > 0 ? '+' : ''}{price.prdy_ctrt}%)
        </div>
        <div className="prev-close">전일 종가: {formatNumber(price.stck_prdy_clpr)}원</div>
      </div>

      <div className="realtime-grid">
        <div className="rt-card">
          <div className="rt-label">시가</div>
          <div className="rt-value">{formatNumber(price.stck_oprc)}원</div>
          <div className={`rt-sub ${oprcSign.cls}`}>
            {oprcSign.symbol} {formatNumber(Math.abs(price.oprc_vrss_prpr))}
            {price.prdy_clpr_vrss_oprc_rate != null && ` (${price.prdy_clpr_vrss_oprc_rate}%)`}
          </div>
        </div>
        <div className="rt-card">
          <div className="rt-label">최고가</div>
          <div className="rt-value high">{formatNumber(price.stck_hgpr)}원</div>
          <div className={`rt-sub ${hgprSign.cls}`}>
            {hgprSign.symbol} {formatNumber(Math.abs(price.hgpr_vrss_prpr))}
            {price.prdy_clpr_vrss_hgpr_rate != null && ` (${price.prdy_clpr_vrss_hgpr_rate}%)`}
          </div>
        </div>
        <div className="rt-card">
          <div className="rt-label">최저가</div>
          <div className="rt-value low">{formatNumber(price.stck_lwpr)}원</div>
          <div className={`rt-sub ${lwprSign.cls}`}>
            {lwprSign.symbol} {formatNumber(Math.abs(price.lwpr_vrss_prpr))}
            {price.prdy_clpr_vrss_lwpr_rate != null && ` (${price.prdy_clpr_vrss_lwpr_rate}%)`}
          </div>
        </div>
        <div className="rt-card">
          <div className="rt-label">기준가</div>
          <div className="rt-value">{formatNumber(price.stck_sdpr)}원</div>
        </div>
        <div className="rt-card">
          <div className="rt-label">상한가</div>
          <div className="rt-value high">{formatNumber(price.stck_mxpr)}원</div>
        </div>
        <div className="rt-card">
          <div className="rt-label">하한가</div>
          <div className="rt-value low">{formatNumber(price.stck_llam)}원</div>
        </div>
      </div>

      <div className="realtime-grid">
        <div className="rt-card">
          <div className="rt-label">누적 거래량</div>
          <div className="rt-value">{formatNumber(price.acml_vol)}주</div>
        </div>
        <div className="rt-card">
          <div className="rt-label">누적 거래대금</div>
          <div className="rt-value">{formatAmount(price.acml_tr_pbmn)}원</div>
        </div>
        <div className="rt-card">
          <div className="rt-label">전일 거래량</div>
          <div className="rt-value">{formatNumber(price.prdy_vol)}주</div>
        </div>
        <div className="rt-card">
          <div className="rt-label">전일 대비 거래량</div>
          <div className="rt-value">{price.prdy_vrss_vol_rate != null ? `${price.prdy_vrss_vol_rate}%` : '-'}</div>
        </div>
      </div>

      <div className="realtime-grid two-col">
        <div className="rt-card">
          <div className="rt-label">증거금 비율</div>
          <div className="rt-value">{price.marg_rate != null ? `${price.marg_rate}%` : '-'}</div>
        </div>
        <div className="rt-card">
          <div className="rt-label">신용 비율</div>
          <div className="rt-value">{price.crdt_rate != null ? `${price.crdt_rate}%` : '-'}</div>
        </div>
        <div className="rt-card">
          <div className="rt-label">신용 가능</div>
          <div className="rt-value">{price.crdt_able_yn === 'Y' ? 'O' : 'X'}</div>
        </div>
        <div className="rt-card">
          <div className="rt-label">종목 상태</div>
          <div className="rt-value">
            {price.trht_yn === 'Y' ? '거래정지' :
             price.mang_issu_yn === 'Y' ? '관리종목' :
             price.sltr_yn === 'Y' ? '정리매매' :
             price.invt_caful_yn === 'Y' ? '투자주의' :
             price.mrkt_warn_cls_code === '01' ? '투자경고' :
             price.mrkt_warn_cls_code === '02' ? '투자위험' :
             price.short_over_yn === 'Y' ? '단기과열' :
             '정상'}
          </div>
        </div>
      </div>

      <div className="realtime-footer">
        <button className="refresh-button" onClick={fetchData}>
          새로고침
        </button>
        <p className="realtime-disclaimer">한국투자증권 Open API 실시간 데이터 (v1_국내주식-054)</p>
      </div>
    </div>
  )
}

export default StockRealTime

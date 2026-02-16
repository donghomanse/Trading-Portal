import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import './StockDetail.css'

function StockDetail() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [stock, setStock] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchStockDetail()
  }, [code])

  const fetchStockDetail = async () => {
    try {
      const response = await fetch(`/api/stocks/${code}`)
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('종목을 찾을 수 없습니다')
        }
        throw new Error('종목 정보를 불러오는데 실패했습니다')
      }
      const data = await response.json()
      setStock(data)
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

  const formatMarketCap = (value) => {
    if (value === null || value === undefined) return '-'
    const eok = Math.floor(value / 100000000)
    return `${formatNumber(eok)}억원`
  }

  const formatPercent = (value) => {
    if (value === null || value === undefined) return '-'
    return `${value.toFixed(2)}%`
  }

  if (loading) {
    return (
      <div className="stock-detail-container">
        <div className="loading">종목 정보를 불러오는 중...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="stock-detail-container">
        <div className="error-container">
          <div className="error-message">{error}</div>
          <button className="back-button" onClick={() => navigate('/stocks')}>
            ← 목록으로 돌아가기
          </button>
        </div>
      </div>
    )
  }

  if (!stock) {
    return null
  }

  return (
    <div className="stock-detail-container">
      <div className="stock-detail-header">
        <button className="back-button" onClick={() => navigate('/stocks')}>
          ← 목록으로
        </button>
        <div className="stock-title">
          <h1>{stock.name}</h1>
          <span className="stock-code-badge">{stock.code}</span>
        </div>
      </div>

      <div className="stock-info-grid">
        <div className="info-card">
          <div className="info-label">시장구분</div>
          <div className="info-value">{stock.market || '-'}</div>
        </div>

        <div className="info-card">
          <div className="info-label">기준가격</div>
          <div className="info-value price">
            {stock.base_price ? `${formatNumber(stock.base_price)}원` : '-'}
          </div>
        </div>

        <div className="info-card">
          <div className="info-label">시가총액</div>
          <div className="info-value">
            {formatMarketCap(stock.market_cap)}
          </div>
        </div>

        <div className="info-card">
          <div className="info-label">ROE (자기자본이익률)</div>
          <div className="info-value">
            {formatPercent(stock.roe)}
          </div>
        </div>

        <div className="info-card">
          <div className="info-label">그룹코드</div>
          <div className="info-value">
            {stock.group_code || '-'}
          </div>
        </div>
      </div>

      <div className="stock-detail-footer">
        <p className="last-updated">
          이 정보는 KOSPI 마스터 데이터를 기준으로 합니다
        </p>
      </div>
    </div>
  )
}

export default StockDetail

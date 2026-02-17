import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Stocks.css'

function Stocks() {
  const [stocks, setStocks] = useState([])
  const [filteredStocks, setFilteredStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [segment, setSegment] = useState('company') // 'company' or 'all'
  const [refreshing, setRefreshing] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchStocks()
  }, [])

  useEffect(() => {
    let filtered = stocks

    // 세그먼트 필터링 (회사 = 그룹코드가 ST)
    if (segment === 'company') {
      filtered = filtered.filter(stock => stock.group_code === 'ST')
    }

    // 검색어 필터링
    if (searchTerm.trim() !== '') {
      filtered = filtered.filter(stock =>
        stock.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    setFilteredStocks(filtered)
  }, [searchTerm, stocks, segment])

  const fetchStocks = async () => {
    try {
      // Fetch all KOSPI stocks (limit set high to get all ~800-900 stocks)
      // TODO: Consider implementing pagination or infinite scroll for better performance
      const response = await fetch('/api/stocks?limit=5000')
      if (!response.ok) {
        throw new Error('Failed to fetch stocks')
      }
      const data = await response.json()
      setStocks(data)
      setFilteredStocks(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    setSearchTerm(e.target.value)
  }

  const clearSearch = () => {
    setSearchTerm('')
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      const response = await fetch('/api/scheduler/update-kospi', { method: 'POST' })
      if (!response.ok) {
        throw new Error('KOSPI 데이터 업데이트에 실패했습니다')
      }
      await fetchStocks()
    } catch (err) {
      setError(err.message)
    } finally {
      setRefreshing(false)
    }
  }

  if (loading) {
    return (
      <div className="stocks-container">
        <div className="loading">KOSPI 종목 정보를 불러오는 중...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="stocks-container">
        <div className="error">오류: {error}</div>
      </div>
    )
  }

  return (
    <div className="stocks-container">
      <div className="stocks-header">
        <h1>KOSPI 종목 조회</h1>
        <button className="back-button" onClick={() => navigate('/')}>
          ← 홈으로
        </button>
      </div>

      <div className="search-section">
        <div className="segment-row">
          <div className="segment-control">
            <button
              className={`segment-button ${segment === 'company' ? 'active' : ''}`}
              onClick={() => setSegment('company')}
            >
              회사
            </button>
            <button
              className={`segment-button ${segment === 'all' ? 'active' : ''}`}
              onClick={() => setSegment('all')}
            >
              전체
            </button>
          </div>
          <button
            className={`refresh-icon-button${refreshing ? ' spinning' : ''}`}
            onClick={handleRefresh}
            disabled={refreshing}
            title="KOSPI 데이터 새로고침"
          >
🔄
          </button>
        </div>
        <div className="search-box">
          <input
            type="text"
            placeholder="종목 코드 또는 종목명으로 검색..."
            value={searchTerm}
            onChange={handleSearch}
            className="search-input"
          />
          {searchTerm && (
            <button className="clear-button" onClick={clearSearch}>
              ✕
            </button>
          )}
        </div>
        <div className="search-info">
          검색 결과: <strong>{filteredStocks.length}</strong>개 / 전체: <strong>{stocks.length}</strong>개
        </div>
      </div>

      {filteredStocks.length === 0 ? (
        <div className="no-stocks">
          <p>검색 결과가 없습니다</p>
          <p className="hint">다른 검색어로 시도해보세요</p>
        </div>
      ) : (
        <div className="stocks-table-container">
          <table className="stocks-table">
            <thead>
              <tr>
                <th>종목 코드</th>
                <th>종목명</th>
              </tr>
            </thead>
            <tbody>
              {filteredStocks.map((stock) => (
                <tr
                  key={stock.code}
                  className="stock-row"
                  onClick={() => navigate(`/stocks/${stock.code}`)}
                >
                  <td className="stock-code">{stock.code}</td>
                  <td className="stock-name">{stock.name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Stocks

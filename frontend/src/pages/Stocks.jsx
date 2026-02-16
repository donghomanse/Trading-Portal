import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Stocks.css'

function Stocks() {
  const [stocks, setStocks] = useState([])
  const [filteredStocks, setFilteredStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    fetchStocks()
  }, [])

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredStocks(stocks)
    } else {
      const filtered = stocks.filter(stock =>
        stock.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredStocks(filtered)
    }
  }, [searchTerm, stocks])

  const fetchStocks = async () => {
    try {
      const response = await fetch('/api/stocks?limit=1000')
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
                <tr key={stock.code} className="stock-row">
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

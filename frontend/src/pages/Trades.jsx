import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './Trades.css'

function Trades() {
  const [trades, setTrades] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchTrades()
  }, [])

  const fetchTrades = async () => {
    try {
      const response = await fetch('/api/trades')
      if (!response.ok) {
        throw new Error('Failed to fetch trades')
      }
      const data = await response.json()
      setTrades(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'executed':
        return '#4caf50'
      case 'pending':
        return '#ff9800'
      case 'cancelled':
        return '#f44336'
      default:
        return '#757575'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ko-KR')
  }

  if (loading) {
    return <div className="trades-container"><div className="loading">Loading trades...</div></div>
  }

  if (error) {
    return <div className="trades-container"><div className="error">Error: {error}</div></div>
  }

  return (
    <div className="trades-container">
      <div className="trades-header">
        <h1>Trading History</h1>
        <button className="back-button" onClick={() => navigate('/')}>
          ← Back to Home
        </button>
      </div>

      {trades.length === 0 ? (
        <div className="no-trades">
          <p>No trades found</p>
          <p className="hint">Create your first trade using the API!</p>
        </div>
      ) : (
        <div className="trades-table-container">
          <table className="trades-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Symbol</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Price</th>
                <th>Total</th>
                <th>Status</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr key={trade.id}>
                  <td>{trade.id}</td>
                  <td className="symbol">{trade.symbol}</td>
                  <td>
                    <span className={`trade-type ${trade.trade_type}`}>
                      {trade.trade_type.toUpperCase()}
                    </span>
                  </td>
                  <td>{trade.quantity.toLocaleString()}</td>
                  <td>${trade.price.toFixed(2)}</td>
                  <td>${(trade.quantity * trade.price).toFixed(2)}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(trade.status) }}
                    >
                      {trade.status}
                    </span>
                  </td>
                  <td className="date">{formatDate(trade.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="trades-summary">
        <p>Total Trades: <strong>{trades.length}</strong></p>
      </div>
    </div>
  )
}

export default Trades

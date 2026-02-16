import { useNavigate } from 'react-router-dom'
import './Home.css'

function Home() {
  const navigate = useNavigate()

  return (
    <div className="home-container">
      <h1>Welcome to Trading System~!!</h1>
      <div className="home-content">
        <p>Manage your trades and track your portfolio</p>
        <button className="view-trades-button" onClick={() => navigate('/trades')}>
          View Trading History →
        </button>
      </div>
    </div>
  )
}

export default Home

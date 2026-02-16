import { useNavigate } from 'react-router-dom'
import './Home.css'

function Home() {
  const navigate = useNavigate()

  return (
    <div className="home-container">
      <h1>Welcome to Trading System~!!</h1>
      <div className="home-content">
        <p>KOSPI 종목 정보를 조회하고 관리하세요</p>
        <button className="view-trades-button" onClick={() => navigate('/stocks')}>
          KOSPI 종목 조회 →
        </button>
      </div>
    </div>
  )
}

export default Home

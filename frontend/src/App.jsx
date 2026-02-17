import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Stocks from './pages/Stocks'
import StockDetail from './pages/StockDetail'
import StockRealTime from './pages/StockRealTime'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/stocks" element={<Stocks />} />
        <Route path="/stocks/:code" element={<StockDetail />} />
        <Route path="/stocks/:code/realtime" element={<StockRealTime />} />
      </Routes>
    </Router>
  )
}

export default App

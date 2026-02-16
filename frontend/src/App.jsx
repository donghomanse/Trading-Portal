import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Trades from './pages/Trades'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/trades" element={<Trades />} />
      </Routes>
    </Router>
  )
}

export default App

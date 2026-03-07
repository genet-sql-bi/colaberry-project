import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from '../pages/Home'
import Analyze from '../pages/Analyze'
import Results from '../pages/Results'

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </BrowserRouter>
  )
}

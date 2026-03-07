import { useNavigate } from 'react-router-dom'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className="page">
      <h1>CareerOS Skill Gap Analyzer</h1>
      <p>Identify the skills you need to land your next role.</p>
      <button onClick={() => navigate('/analyze')}>Start Analysis</button>
    </div>
  )
}

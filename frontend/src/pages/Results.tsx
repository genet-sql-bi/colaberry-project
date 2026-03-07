import { useLocation, useNavigate } from 'react-router-dom'

interface SkillCategory {
  skill: string
  category: string
  priority: 'High' | 'Medium' | 'Low'
}

interface AnalysisResult {
  categories: SkillCategory[]
}

const PRIORITY_ORDER: Record<string, number> = { High: 0, Medium: 1, Low: 2 }

const PRIORITY_CLASS: Record<string, string> = {
  High: 'badge badge--high',
  Medium: 'badge badge--medium',
  Low: 'badge badge--low',
}

function groupBy<T>(items: T[], key: keyof T): Record<string, T[]> {
  return items.reduce<Record<string, T[]>>((acc, item) => {
    const k = String(item[key])
    ;(acc[k] ??= []).push(item)
    return acc
  }, {})
}

export default function Results() {
  const navigate = useNavigate()
  const location = useLocation()
  const state = location.state as { results?: AnalysisResult } | null
  const results = state?.results

  if (!results) {
    return (
      <div className="page">
        <h1>Results</h1>
        <p className="placeholder">No results yet. Run an analysis first.</p>
        <button onClick={() => navigate('/analyze')}>Start Analysis</button>
      </div>
    )
  }

  if (results.categories.length === 0) {
    return (
      <div className="page">
        <h1>Results</h1>
        <p className="no-gaps">No skill gaps found — your profile matches the job description.</p>
        <button onClick={() => navigate('/analyze')}>Run Another Analysis</button>
      </div>
    )
  }

  const sorted = [...results.categories].sort(
    (a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority],
  )
  const groups = groupBy(sorted, 'category')
  const categoryOrder = ['Technical', 'Soft Skill', 'Tool/Other']
  const orderedGroups = categoryOrder.filter((c) => groups[c])

  return (
    <div className="page">
      <h1>Skill Gap Results</h1>
      <p className="results-summary">
        {results.categories.length} skill gap{results.categories.length !== 1 ? 's' : ''} identified
      </p>

      {orderedGroups.map((category) => (
        <div key={category} className="category-section">
          <h2 className="category-heading">{category}</h2>
          <ul className="skill-list">
            {groups[category].map(({ skill, priority }) => (
              <li key={skill} className="skill-item">
                <span className="skill-name">{skill}</span>
                <span className={PRIORITY_CLASS[priority]}>{priority}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}

      <button onClick={() => navigate('/analyze')}>Run Another Analysis</button>
    </div>
  )
}

import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Analyze() {
  const navigate = useNavigate()
  const [jd, setJd] = useState('')
  const [skills, setSkills] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const resumeRef = useRef<HTMLInputElement>(null)
  const linkedinRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!jd.trim()) {
      setError('Please paste a job description.')
      return
    }

    setLoading(true)
    try {
      const form = new FormData()
      form.append('jd_text', jd.trim())
      form.append('skills', skills.trim())
      if (resumeRef.current?.files?.[0]) {
        form.append('resume_file', resumeRef.current.files[0])
      }
      if (linkedinRef.current?.files?.[0]) {
        form.append('linkedin_file', linkedinRef.current.files[0])
      }

      const res = await fetch('http://localhost:8000/upload-analyze', {
        method: 'POST',
        body: form,
      })

      if (!res.ok) {
        const detail = await res.text()
        throw new Error(detail || `Server error ${res.status}`)
      }

      const data = await res.json()
      navigate('/results', { state: { results: data } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error. Is the API server running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Analyze Your Skills</h1>
      <form onSubmit={handleSubmit} className="form">
        <label htmlFor="jd">Job Description</label>
        <textarea
          id="jd"
          value={jd}
          onChange={(e) => setJd(e.target.value)}
          placeholder="Paste the job description here..."
          rows={6}
        />

        <label htmlFor="skills">Your Skills (optional)</label>
        <textarea
          id="skills"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
          placeholder="e.g. Python, SQL, AWS"
          rows={3}
        />

        <label htmlFor="resume">Resume PDF (optional)</label>
        <input id="resume" type="file" accept=".pdf" ref={resumeRef} />

        <label htmlFor="linkedin">LinkedIn Profile PDF (optional)</label>
        <input id="linkedin" type="file" accept=".pdf" ref={linkedinRef} />

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>
    </div>
  )
}

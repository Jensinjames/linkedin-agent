import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient'
import { Table, type Column, Pagination } from '../components'
import { useNavigate, Link } from 'react-router-dom'

interface Team {
  id: number
  name: string
}

/**
 * Displays a paginated table of teams, fetching data from an API with authentication.
 *
 * Fetches the list of teams for the current page using an authenticated API request, and renders the results in a table with pagination controls.
 */
export default function Teams() {
  const [teams, setTeams] = useState<Team[]>([])
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const signOut = async () => {
    await supabase.auth.signOut()
    navigate('/login')
  }

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const session = await supabase.auth.getSession()
        const token = session.data.session?.access_token
        
        if (!token) {
          navigate('/login')
          return
        }

        const res = await fetch(`${import.meta.env.VITE_API_BASE}/teams?page=${page}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        if (res.ok) {
          setTeams(await res.json())
        } else {
          setError('Failed to load teams')
        }
      } catch {
        setError('Network error')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [page, navigate])

  const columns: Column<Team>[] = [
    { header: 'ID', accessor: 'id' },
    { header: 'Name', accessor: 'name' }
  ]

  if (loading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">Teams</h1>
        </div>
        <p>Loading teams...</p>
      </div>
    )
  }

  return (
    <div className="page-container">
      <div className="nav">
        <h1 className="page-title">Teams</h1>
        <div className="nav-links">
          <Link to="/credits" className="nav-link">Credits</Link>
          <button className="btn btn-secondary" onClick={signOut}>
            Sign Out
          </button>
        </div>
      </div>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '1rem' }}>
          Error: {error}
        </div>
      )}
      
      <Table columns={columns} data={teams} />
      <Pagination page={page} totalPages={10} onPageChange={setPage} />
    </div>
  )
}

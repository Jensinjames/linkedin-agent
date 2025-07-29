import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient'
import { Link, useNavigate } from 'react-router-dom'

/**
 * Displays the user's remaining credits by fetching the current balance from an authenticated API endpoint.
 *
 * Retrieves the user's session and access token, requests the current credits from the backend, and updates the display accordingly.
 */
export default function Credits() {
    const [credits, setCredits] = useState<number>(0)
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

                const res = await fetch(`${import.meta.env.VITE_API_BASE}/credits`, {
                    headers: {Authorization: `Bearer ${token}`}
                })

                if (res.ok) {
                    const data = await res.json()
                    setCredits(data.credits)
                } else {
                    setError('Failed to load credits')
                }
            } catch {
                setError('Network error')
            } finally {
                setLoading(false)
            }
        }
        load()
    }, [navigate])

    if (loading) {
        return (
            <div className="page-container">
                <div className="page-header">
                    <h1 className="page-title">Credits</h1>
                </div>
                <p>Loading credits...</p>
            </div>
        )
    }

    return (
        <div className="page-container">
            <div className="nav">
                <h1 className="page-title">Credits</h1>
                <div className="nav-links">
                    <Link to="/teams" className="nav-link">Teams</Link>
                    <button className="btn btn-secondary" onClick={signOut}>
                        Sign Out
                    </button>
                </div>
            </div>

            {error && (
                <div style={{color: 'red', marginBottom: '1rem'}}>
                    Error: {error}
                </div>
            )}

            <div className="credits-display">
                <span className="credits-number">{credits.toLocaleString()}</span>
                <p>Remaining Credits</p>
            </div>
        </div>
    )
}

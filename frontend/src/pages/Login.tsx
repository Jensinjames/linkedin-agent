import { useState } from 'react'
import { supabase } from '../supabaseClient'
import { useNavigate } from 'react-router-dom'

/**
 * Renders an admin login form that authenticates users using email and password.
 *
 * On successful authentication, navigates to the teams page; otherwise, displays an error alert.
 */
export default function Login() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()

    const signIn = async () => {
        setLoading(true)
        try {
            const {error} = await supabase.auth.signInWithPassword({email, password})
            if (!error) {
                navigate('/teams')
            } else {
                alert(error.message)
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="page-container">
            <div className="login-container">
                <h2>Admin Login</h2>
                <div className="form-group">
                    <input
                        className="form-input"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="Email"
                        type="email"
                    />
                </div>
                <div className="form-group">
                    <input
                        className="form-input"
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        placeholder="Password"
                    />
                </div>
                <button
                    className="btn btn-primary"
                    onClick={signIn}
                    disabled={loading}
                >
                    {loading ? 'Signing in...' : 'Login'}
                </button>
            </div>
        </div>
    )
}

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
  const navigate = useNavigate()

  const signIn = async () => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (!error) navigate('/teams')
    else alert(error.message)
  }

  return (
    <div>
      <h2>Admin Login</h2>
      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="email" />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="password" />
      <button onClick={signIn}>Login</button>
    </div>
  )
}

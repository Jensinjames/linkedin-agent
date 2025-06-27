import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient'
import { useNavigate } from 'react-router-dom'

export const RequireAdmin: React.FC<{children: JSX.Element}> = ({ children }) => {
  const navigate = useNavigate()
  const [allowed, setAllowed] = useState<boolean | null>(null)

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_, session) => {
      check(session)
    })
    check(supabase.auth.getSession().data?.session)
    return () => { subscription.unsubscribe() }
  }, [])

  const check = (session: any) => {
    if (!session) {
      navigate('/login')
      return
    }
    const roles = session.user.app_metadata?.roles || []
    if (roles.includes('admin')) {
      setAllowed(true)
    } else {
      navigate('/login')
    }
  }

  if (allowed) return children
  return null
}

import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../supabaseClient'
import { useNavigate } from 'react-router-dom'
import type { Session } from '@supabase/supabase-js'

export const RequireAdmin: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const navigate = useNavigate()
  const [allowed, setAllowed] = useState<boolean | null>(null)

  const check = useCallback((session: Session | null) => {
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
  }, [navigate])

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_, session) => {
      check(session)
    })
    
    const initCheck = async () => {
      const { data } = await supabase.auth.getSession()
      check(data?.session)
    }
    initCheck()
    
    return () => { subscription.unsubscribe() }
  }, [check])

  if (allowed) return children
  return null
}

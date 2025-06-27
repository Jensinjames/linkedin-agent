import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient'

export default function Credits() {
  const [credits, setCredits] = useState<number>(0)

  useEffect(() => {
    const load = async () => {
      const session = await supabase.auth.getSession()
      const token = session.data.session?.access_token
      const res = await fetch(`${import.meta.env.VITE_API_BASE}/credits`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setCredits(data.credits)
      }
    }
    load()
  }, [])

  return (
    <div>
      <h2>Credits</h2>
      <p>Remaining credits: {credits}</p>
    </div>
  )
}

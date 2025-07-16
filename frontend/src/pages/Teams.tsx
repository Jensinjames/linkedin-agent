import { useEffect, useState } from 'react'
import { supabase } from '../supabaseClient'
import { Table, type Column, Pagination } from '../components'

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

  useEffect(() => {
    const load = async () => {
      const session = await supabase.auth.getSession()
      const token = session.data.session?.access_token
      const res = await fetch(`${import.meta.env.VITE_API_BASE}/teams?page=${page}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        setTeams(await res.json())
      }
    }
    load()
  }, [page])

  const columns: Column<Team>[] = [
    { header: 'ID', accessor: 'id' },
    { header: 'Name', accessor: 'name' }
  ]

  return (
    <div>
      <h2>Teams</h2>
      <Table columns={columns} data={teams} />
      <Pagination page={page} totalPages={10} onPageChange={setPage} />
    </div>
  )
}

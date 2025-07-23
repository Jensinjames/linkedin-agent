import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Teams from './pages/Teams'
import Credits from './pages/Credits'
import Login from './pages/Login'
import { RequireAdmin } from './components'
import './App.css'

/**
 * Sets up the application's client-side routing and access control.
 *
 * Defines routes for login, teams, and credits pages, applying admin access restrictions to the teams and credits routes. Unmatched routes redirect to the login page.
 *
 * @returns The application's routing structure as a React element.
 */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/teams" element={<RequireAdmin><Teams /></RequireAdmin>} />
        <Route path="/credits" element={<RequireAdmin><Credits /></RequireAdmin>} />
        <Route path="*" element={<Login />} />
      </Routes>
    </BrowserRouter>
  )
}

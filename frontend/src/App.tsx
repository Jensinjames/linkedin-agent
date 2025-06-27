import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Teams from './pages/Teams'
import Credits from './pages/Credits'
import Login from './pages/Login'
import { RequireAdmin } from './components'

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

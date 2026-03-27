import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage.jsx'
import AuthPage from './pages/AuthPage.jsx'
import DashboardLayout from './components/dashboard/DashboardLayout.jsx'
import DashboardOverview from './components/dashboard/DashboardOverview.jsx'
import DashboardCalendar from './components/dashboard/DashboardCalendar.jsx'
import DashboardPatients from './components/dashboard/DashboardPatients.jsx'
import DashboardProfile from './components/dashboard/DashboardProfile.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<DashboardOverview />} />
          <Route path="agenda" element={<DashboardCalendar />} />
          <Route path="pacientes" element={<DashboardPatients />} />
          <Route path="perfil" element={<DashboardProfile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)

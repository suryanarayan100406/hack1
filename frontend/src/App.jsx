import { useState, useEffect } from 'react'
import Login from './components/Login'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import MapView from './components/MapView'
import Upload from './components/Upload'
import Analysis from './components/Analysis'
import Reports from './components/Reports'
import Alerts from './components/Alerts'
import AdminPanel from './components/AdminPanel'
import APIPortal from './components/APIPortal'
import CitizenWatch from './components/CitizenWatch'

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [activePage, setActivePage] = useState('dashboard')

    useEffect(() => {
        const auth = localStorage.getItem('auth')
        if (auth === 'true') setIsAuthenticated(true)
    }, [])

    const handleLogin = () => {
        localStorage.setItem('auth', 'true')
        setIsAuthenticated(true)
    }

    const handleLogout = () => {
        localStorage.removeItem('auth')
        setIsAuthenticated(false)
        setActivePage('dashboard')
    }

    if (!isAuthenticated) {
        return <Login onLogin={handleLogin} />
    }

    const renderPage = () => {
        switch (activePage) {
            case 'dashboard': return <Dashboard onNavigate={setActivePage} />
            case 'map': return <MapView />
            case 'upload': return <Upload onNavigate={setActivePage} />
            case 'analysis': return <Analysis />
            case 'reports': return <Reports />
            case 'alerts': return <Alerts />
            case 'admin': return <AdminPanel onNavigate={setActivePage} />
            case 'api': return <APIPortal />
            case 'citizen': return <CitizenWatch />
            default: return <Dashboard onNavigate={setActivePage} />
        }
    }

    return (
        <div className="app-layout">
            <Sidebar activePage={activePage} onNavigate={setActivePage} onLogout={handleLogout} />
            <div className="main-content">
                <div className="page-content">
                    {renderPage()}
                </div>
            </div>
        </div>
    )
}

export default App

import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import MapView from './components/MapView'
import Upload from './components/Upload'
import Analysis from './components/Analysis'
import Reports from './components/Reports'
import Alerts from './components/Alerts'
import AdminPanel from './components/AdminPanel'

function App() {
    const [activePage, setActivePage] = useState('dashboard')

    const renderPage = () => {
        switch (activePage) {
            case 'dashboard': return <Dashboard onNavigate={setActivePage} />
            case 'map': return <MapView />
            case 'upload': return <Upload onNavigate={setActivePage} />
            case 'analysis': return <Analysis />
            case 'reports': return <Reports />
            case 'alerts': return <Alerts />
            case 'admin': return <AdminPanel onNavigate={setActivePage} />
            default: return <Dashboard onNavigate={setActivePage} />
        }
    }

    return (
        <div className="app-layout">
            <Sidebar activePage={activePage} onNavigate={setActivePage} />
            <div className="main-content">
                <div className="page-content">
                    {renderPage()}
                </div>
            </div>
        </div>
    )
}

export default App

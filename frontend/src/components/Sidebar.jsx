const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'map', label: 'Map View', icon: '🗺️' },
    { id: 'upload', label: 'Upload & Analyze', icon: '📤' },
    { id: 'analysis', label: 'Analysis Results', icon: '🔍' },
    { id: 'reports', label: 'Compliance Reports', icon: '📋' },
    { id: 'alerts', label: 'Alerts', icon: '🔔' },
    { id: 'admin', label: 'Admin Panel', icon: '🛠️' },
]

function Sidebar({ activePage, onNavigate }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <h1>🛰️ Land Sentinel</h1>
                <p>CSIDC Monitoring System</p>
            </div>

            <nav className="sidebar-nav">
                {navItems.map(item => (
                    <div
                        key={item.id}
                        className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                        onClick={() => onNavigate(item.id)}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span>{item.label}</span>
                    </div>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-status">
                    <span className="status-dot"></span>
                    <span>System Active • v1.0</span>
                </div>
            </div>
        </aside>
    )
}

export default Sidebar

const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'map', label: 'Map View', icon: '🗺️' },
    { id: 'upload', label: 'Upload & Analyze', icon: '📤' },
    { id: 'analysis', label: 'Analysis Results', icon: '🔍' },
    { id: 'reports', label: 'Compliance Reports', icon: '📋' },
    { id: 'alerts', label: 'Alerts', icon: '🔔' },
    { id: 'api', label: 'Developer API', icon: '🔌' },
    { id: 'admin', label: 'Admin Panel', icon: '🛠️' },
    { id: 'citizen', label: 'Citizen Watch', icon: '👁️' },
]

function Sidebar({ activePage, onNavigate, onLogout }) {
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
                <div
                    className="nav-item"
                    onClick={() => onLogout && onLogout()}
                    style={{ marginBottom: 12, color: '#ef4444', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: 12, cursor: onLogout ? 'pointer' : 'default', opacity: onLogout ? 1 : 0.5 }}
                >
                    <span className="nav-icon">🚪</span>
                    <span>Logout</span>
                </div>
                <div className="sidebar-status">
                    <span className="status-dot"></span>
                    <span>System Active • v1.0</span>
                </div>
            </div>
        </aside>
    )
}

export default Sidebar

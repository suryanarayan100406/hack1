import { useState, useEffect, useCallback } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import MapView from './MapView'

const COLORS = {
    compliant: '#10b981',
    violation: '#ef4444',
    vacant: '#8b5cf6',
}

import { getApiUrl } from '../config'

function Dashboard({ onNavigate }) {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 10000) // 10s timeout

        fetch(getApiUrl('/api/demo-data'), { signal: controller.signal })
            .then(res => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
                return res.json()
            })
            .then(d => {
                setData(d)
                setLoading(false)
                clearTimeout(timeoutId)
            })
            .catch(err => {
                console.error("Dashboard fetch error:", err)
                setLoading(false)
            })

        return () => clearTimeout(timeoutId)
    }, [])

    if (loading) return <div className="spinner"></div>
    if (!data) return <div className="empty-state"><h3>Could not load data</h3></div>

    const { stats, alerts, areas } = data

    const pieData = [
        { name: 'Compliant', value: stats.compliant, color: COLORS.compliant },
        { name: 'Violations', value: stats.violations, color: COLORS.violation },
        { name: 'Vacant', value: stats.vacant, color: COLORS.vacant },
    ]

    const areaChartData = Object.values(stats.area_stats).map(a => ({
        name: a.name.replace(' Industrial Area', ''),
        Compliant: a.compliant,
        Violations: a.violations,
        Vacant: a.vacant,
        'Avg Score': a.avg_compliance,
    }))

    const recentAlerts = [...alerts]
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 5)

    const handleDistrictSelect = useCallback((id) => {
        // We need to pass the selected ID to the upload page
        // Since onNavigate just switches tabs, we might need a way to pass params
        // For now, we'll store it in localStorage or use a global context if available.
        // Or simpler: The Upload component can check URL params or a simple prop if we could pass it.
        // Assuming onNavigate just takes a string.
        console.log("District selected:", id)
        localStorage.setItem('selected_registry_id', id);
        onNavigate('upload');
    }, [onNavigate])

    return (
        <div>
            <div className="page-header">
                <h2>📊 Command Center</h2>
                <p>Real-time monitoring of industrial land allotments across Chhattisgarh</p>
            </div>

            {/* KPI Cards */}
            <div className="kpi-grid" style={{ marginTop: 24 }}>
                <div className="kpi-card primary animate-in animate-in-delay-1">
                    <div className="kpi-header">
                        <span className="kpi-label">Total Plots</span>
                        <span className="kpi-icon">🏭</span>
                    </div>
                    <div className="kpi-value">{stats.total_plots}</div>
                    <div className="kpi-sub">Across {areas.length} industrial areas</div>
                </div>

                <div className="kpi-card success animate-in animate-in-delay-2">
                    <div className="kpi-header">
                        <span className="kpi-label">Compliant</span>
                        <span className="kpi-icon">✅</span>
                    </div>
                    <div className="kpi-value" style={{ color: '#10b981' }}>{stats.compliant}</div>
                    <div className="kpi-sub">{((stats.compliant / stats.total_plots) * 100).toFixed(0)}% of total plots</div>
                </div>

                <div className="kpi-card danger animate-in animate-in-delay-3">
                    <div className="kpi-header">
                        <span className="kpi-label">Violations</span>
                        <span className="kpi-icon">🚨</span>
                    </div>
                    <div className="kpi-value" style={{ color: '#ef4444' }}>{stats.violations}</div>
                    <div className="kpi-sub">{stats.pending_alerts} pending alerts</div>
                </div>

                <div className="kpi-card warning animate-in animate-in-delay-4">
                    <div className="kpi-header">
                        <span className="kpi-label">Avg Compliance</span>
                        <span className="kpi-icon">📈</span>
                    </div>
                    <div className="kpi-value" style={{ color: stats.avg_compliance_score > 60 ? '#10b981' : '#f59e0b' }}>
                        {stats.avg_compliance_score}%
                    </div>
                    <div className="kpi-sub">Overall compliance score</div>
                </div>
            </div>

            {/* Interactive Map */}
            <div className="chart-card animate-in animate-in-delay-2" style={{ marginTop: 24, marginBottom: 24 }}>
                <h3 style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span>🗺️ Industrial Districts Map</span>
                    <span style={{ fontSize: 13, fontWeight: 400, color: '#94a3b8' }}>Click a district to analyze</span>
                </h3>
                <div style={{ height: 400, marginTop: 16 }}>
                    <MapView onSelectDistrict={handleDistrictSelect} />
                </div>
            </div>

            {/* Charts Row */}
            <div className="dashboard-grid">
                <div className="chart-card animate-in">
                    <h3>📊 Area-wise Compliance</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={areaChartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                            <Tooltip
                                contentStyle={{
                                    background: '#1e293b',
                                    border: '1px solid rgba(148,163,184,0.2)',
                                    borderRadius: 8,
                                    color: '#f1f5f9',
                                    fontSize: 13,
                                }}
                            />
                            <Bar dataKey="Compliant" fill="#10b981" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="Violations" fill="#ef4444" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="Vacant" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="chart-card animate-in">
                    <h3>🎯 Status Distribution</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <PieChart>
                            <Pie
                                data={pieData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={100}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {pieData.map((entry, i) => (
                                    <Cell key={i} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    background: '#1e293b',
                                    border: '1px solid rgba(148,163,184,0.2)',
                                    borderRadius: 8,
                                    color: '#f1f5f9',
                                }}
                            />
                            <Legend
                                formatter={(value) => <span style={{ color: '#94a3b8', fontSize: 13 }}>{value}</span>}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Recent Alerts + Quick Actions */}
            <div className="dashboard-grid">
                <div className="chart-card">
                    <h3>🔔 Recent Alerts</h3>
                    <div className="alerts-list">
                        {recentAlerts.map(alert => (
                            <div key={alert.id} className="alert-item" onClick={() => onNavigate('alerts')}>
                                <div className={`alert-severity ${alert.severity}`}></div>
                                <div className="alert-content">
                                    <div className="alert-title">{alert.plot_id} — {alert.area}</div>
                                    <div className="alert-msg">{alert.message}</div>
                                    <div className="alert-meta">
                                        {new Date(alert.timestamp).toLocaleDateString('en-IN', {
                                            day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
                                        })}
                                        {alert.acknowledged && ' • ✓ Acknowledged'}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="chart-card">
                    <h3>⚡ Quick Actions</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 8 }}>
                        <button className="btn-primary" onClick={() => onNavigate('map')} style={{ width: '100%' }}>
                            🗺️ View Interactive Map
                        </button>
                        <button className="btn-primary" onClick={() => onNavigate('upload')} style={{ width: '100%', background: 'linear-gradient(135deg, #059669, #10b981)' }}>
                            📤 Upload New Images
                        </button>
                        <button className="btn-primary" onClick={() => onNavigate('reports')} style={{ width: '100%', background: 'linear-gradient(135deg, #d97706, #f59e0b)' }}>
                            📋 View Full Reports
                        </button>

                        {/* Industrial area quick stats */}
                        <div style={{ marginTop: 8 }}>
                            <h4 style={{ fontSize: 14, color: '#94a3b8', marginBottom: 10 }}>Industrial Areas</h4>
                            {areas.map(area => (
                                <div key={area.id} style={{
                                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                    padding: '8px 0', borderBottom: '1px solid rgba(148,163,184,0.1)',
                                    fontSize: 13
                                }}>
                                    <span>{area.name}</span>
                                    <span style={{ color: '#64748b', fontSize: 12 }}>{area.total_area_acres} acres</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard

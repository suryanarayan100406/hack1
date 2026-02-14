import { useState, useEffect } from 'react'
import { getApiUrl } from '../config'

function Alerts() {
    const [alerts, setAlerts] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all')

    useEffect(() => {
        fetch(getApiUrl('/api/alerts'))
            .then(res => res.json())
            .then(data => {
                setAlerts(data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)))
                setLoading(false)
            })
            .catch(() => setLoading(false))
    }, [])

    const filtered = alerts.filter(a => {
        if (filter === 'all') return true
        if (filter === 'unacknowledged') return !a.acknowledged
        return a.severity === filter
    })

    const toggleAcknowledge = (id) => {
        setAlerts(prev => prev.map(a =>
            a.id === id ? { ...a, acknowledged: !a.acknowledged } : a
        ))
    }

    const severityIcon = (severity) => {
        switch (severity) {
            case 'critical': return '🔴'
            case 'warning': return '🟡'
            case 'moderate': return '🟠'
            default: return '⚪'
        }
    }

    const typeLabel = (type) => {
        switch (type) {
            case 'encroachment': return '🚧 Encroachment'
            case 'unauthorized_construction': return '🏗️ Unauthorized Construction'
            case 'unused_land': return '🏚️ Unused Land'
            default: return type
        }
    }

    if (loading) return <div className="spinner"></div>

    const unackCount = alerts.filter(a => !a.acknowledged).length

    return (
        <div>
            <div className="page-header">
                <h2>🔔 Alerts & Notifications</h2>
                <p>Real-time violation alerts from satellite monitoring analysis</p>
            </div>

            <div style={{ marginTop: 24 }}>
                {/* Summary Bar */}
                <div className="kpi-grid" style={{ marginBottom: 20 }}>
                    <div className="kpi-card danger">
                        <div className="kpi-header"><span className="kpi-label">Critical</span><span>🔴</span></div>
                        <div className="kpi-value">{alerts.filter(a => a.severity === 'critical').length}</div>
                    </div>
                    <div className="kpi-card warning">
                        <div className="kpi-header"><span className="kpi-label">Warnings</span><span>🟡</span></div>
                        <div className="kpi-value">{alerts.filter(a => a.severity === 'warning').length}</div>
                    </div>
                    <div className="kpi-card info">
                        <div className="kpi-header"><span className="kpi-label">Moderate</span><span>🟠</span></div>
                        <div className="kpi-value">{alerts.filter(a => a.severity === 'moderate').length}</div>
                    </div>
                    <div className="kpi-card primary">
                        <div className="kpi-header"><span className="kpi-label">Pending</span><span>📬</span></div>
                        <div className="kpi-value">{unackCount}</div>
                        <div className="kpi-sub">Require attention</div>
                    </div>
                </div>

                {/* Filters */}
                <div className="filter-bar">
                    {['all', 'critical', 'warning', 'moderate', 'unacknowledged'].map(f => (
                        <button
                            key={f}
                            className={`filter-btn ${filter === f ? 'active' : ''}`}
                            onClick={() => setFilter(f)}
                        >
                            {f === 'all' ? '📊 All' :
                                f === 'critical' ? '🔴 Critical' :
                                    f === 'warning' ? '🟡 Warning' :
                                        f === 'moderate' ? '🟠 Moderate' :
                                            '📬 Pending'}
                        </button>
                    ))}
                    <span style={{ marginLeft: 'auto', fontSize: 13, color: '#64748b' }}>
                        {filtered.length} alerts
                    </span>
                </div>

                {/* Alert Cards */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {filtered.map(alert => (
                        <div key={alert.id} className="glass-card animate-in" style={{
                            padding: 0,
                            overflow: 'hidden',
                            opacity: alert.acknowledged ? 0.7 : 1,
                        }}>
                            <div style={{ display: 'flex' }}>
                                {/* Severity Bar */}
                                <div style={{
                                    width: 5,
                                    background: alert.severity === 'critical' ? '#ef4444' :
                                        alert.severity === 'warning' ? '#f59e0b' : '#06b6d4',
                                    flexShrink: 0,
                                }}></div>

                                <div style={{ flex: 1, padding: '16px 20px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                                                <span>{severityIcon(alert.severity)}</span>
                                                <span style={{ fontSize: 14, fontWeight: 700 }}>{alert.plot_id}</span>
                                                <span style={{
                                                    fontSize: 11, padding: '2px 8px', borderRadius: 12,
                                                    background: alert.severity === 'critical' ? 'rgba(239,68,68,0.15)' :
                                                        alert.severity === 'warning' ? 'rgba(245,158,11,0.15)' : 'rgba(6,182,212,0.15)',
                                                    color: alert.severity === 'critical' ? '#ef4444' :
                                                        alert.severity === 'warning' ? '#f59e0b' : '#06b6d4',
                                                    fontWeight: 600, textTransform: 'uppercase',
                                                }}>
                                                    {alert.severity}
                                                </span>
                                            </div>
                                            <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}>
                                                {typeLabel(alert.type)}
                                            </div>
                                            <div style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.5 }}>
                                                {alert.message}
                                            </div>
                                            <div style={{ fontSize: 12, color: '#64748b', marginTop: 6 }}>
                                                📍 {alert.area} • 🕐{' '}
                                                {new Date(alert.timestamp).toLocaleDateString('en-IN', {
                                                    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
                                                })}
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => toggleAcknowledge(alert.id)}
                                            style={{
                                                padding: '6px 14px', borderRadius: 8,
                                                border: '1px solid',
                                                borderColor: alert.acknowledged ? '#10b981' : '#64748b',
                                                background: alert.acknowledged ? 'rgba(16,185,129,0.1)' : 'transparent',
                                                color: alert.acknowledged ? '#10b981' : '#94a3b8',
                                                fontSize: 12, fontWeight: 600, cursor: 'pointer',
                                                fontFamily: 'inherit', whiteSpace: 'nowrap',
                                                transition: 'all 0.2s ease',
                                            }}
                                        >
                                            {alert.acknowledged ? '✅ Acknowledged' : 'Mark Done'}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Alerts

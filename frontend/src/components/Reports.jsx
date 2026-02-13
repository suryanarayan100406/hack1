import { useState, useEffect } from 'react'

function Reports() {
    const [plots, setPlots] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all')
    const [areas, setAreas] = useState([])
    const [areaFilter, setAreaFilter] = useState('all')

    useEffect(() => {
        fetch('/api/demo-data')
            .then(res => res.json())
            .then(data => {
                setPlots(data.plots)
                setAreas(data.areas)
                setLoading(false)
            })
            .catch(() => setLoading(false))
    }, [])

    const filteredPlots = plots.filter(p => {
        if (filter !== 'all' && p.status !== filter) return false
        if (areaFilter !== 'all' && p.area_id !== areaFilter) return false
        return true
    })

    const exportCSV = () => {
        const headers = ['Plot ID', 'Name', 'Area', 'Status', 'Violation Type', 'Allotted (sqm)', 'Current (sqm)', 'Deviation %', 'Compliance Score', 'Lease Status', 'Last Payment', 'Last Checked']
        const rows = filteredPlots.map(p => [
            p.id, p.name, p.area_id, p.status, p.violation_type || 'N/A',
            p.allotted_area_sqm, p.current_area_sqm, p.deviation_pct,
            p.compliance_score, p.lease_status, p.last_payment, p.last_checked
        ])

        const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
        const blob = new Blob([csv], { type: 'text/csv' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `compliance_report_${new Date().toISOString().split('T')[0]}.csv`
        a.click()
    }

    const getScoreClass = (score) => {
        if (score >= 70) return 'score-high'
        if (score >= 40) return 'score-mid'
        return 'score-low'
    }

    const getBarColor = (score) => {
        if (score >= 70) return '#10b981'
        if (score >= 40) return '#f59e0b'
        return '#ef4444'
    }

    if (loading) return <div className="spinner"></div>

    return (
        <div>
            <div className="page-header">
                <h2>📋 Compliance Reports</h2>
                <p>Detailed compliance status of all monitored industrial plots</p>
            </div>

            <div style={{ marginTop: 24 }}>
                {/* Filters */}
                <div className="filter-bar">
                    {['all', 'compliant', 'violation', 'vacant'].map(status => (
                        <button
                            key={status}
                            className={`filter-btn ${filter === status ? 'active' : ''}`}
                            onClick={() => setFilter(status)}
                        >
                            {status === 'all' ? '📊 All' :
                                status === 'compliant' ? '✅ Compliant' :
                                    status === 'violation' ? '🚨 Violations' : '🏚️ Vacant'}
                        </button>
                    ))}

                    <span style={{ color: '#64748b', margin: '0 8px' }}>|</span>

                    <select
                        className="form-input"
                        style={{ width: 200, padding: '6px 12px', fontSize: 13 }}
                        value={areaFilter}
                        onChange={e => setAreaFilter(e.target.value)}
                    >
                        <option value="all">All Areas</option>
                        {areas.map(a => (
                            <option key={a.id} value={a.id}>{a.name}</option>
                        ))}
                    </select>

                    <button className="export-btn" onClick={exportCSV}>
                        📥 Export CSV
                    </button>
                </div>

                {/* Summary */}
                <div style={{ display: 'flex', gap: 16, marginBottom: 16, fontSize: 13, color: '#94a3b8' }}>
                    <span>Showing {filteredPlots.length} of {plots.length} plots</span>
                    <span>•</span>
                    <span style={{ color: '#10b981' }}>{filteredPlots.filter(p => p.status === 'compliant').length} Compliant</span>
                    <span>•</span>
                    <span style={{ color: '#ef4444' }}>{filteredPlots.filter(p => p.status === 'violation').length} Violations</span>
                    <span>•</span>
                    <span style={{ color: '#8b5cf6' }}>{filteredPlots.filter(p => p.status === 'vacant').length} Vacant</span>
                </div>

                {/* Table */}
                <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
                    <div className="reports-table-wrapper">
                        <table className="reports-table">
                            <thead>
                                <tr>
                                    <th>Plot ID</th>
                                    <th>Name</th>
                                    <th>Area</th>
                                    <th>Status</th>
                                    <th>Deviation</th>
                                    <th>Compliance</th>
                                    <th>Lease</th>
                                    <th>Last Checked</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredPlots.map(plot => (
                                    <tr key={plot.id}>
                                        <td style={{ fontWeight: 600, color: '#a5b4fc' }}>{plot.id}</td>
                                        <td>{plot.name}</td>
                                        <td style={{ color: '#94a3b8' }}>
                                            {areas.find(a => a.id === plot.area_id)?.name.replace(' Industrial Area', '') || plot.area_id}
                                        </td>
                                        <td>
                                            <span className={`status-badge ${plot.status}`}>
                                                {plot.status === 'compliant' ? '✅' : plot.status === 'violation' ? '🚨' : '🏚️'} {plot.status}
                                            </span>
                                        </td>
                                        <td style={{
                                            color: plot.deviation_pct > 10 ? '#ef4444' : plot.deviation_pct > 0 ? '#f59e0b' : '#10b981',
                                            fontWeight: 600,
                                        }}>
                                            {plot.deviation_pct}%
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                                <span className={getScoreClass(plot.compliance_score)} style={{ fontWeight: 600 }}>
                                                    {plot.compliance_score}
                                                </span>
                                                <div className="compliance-bar">
                                                    <div
                                                        className="compliance-fill"
                                                        style={{
                                                            width: `${plot.compliance_score}%`,
                                                            background: getBarColor(plot.compliance_score),
                                                        }}
                                                    ></div>
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <span style={{
                                                color: plot.lease_status === 'current' ? '#10b981' : '#ef4444',
                                                fontWeight: 500,
                                            }}>
                                                {plot.lease_status === 'current' ? '✅' : '⚠️'} {plot.lease_status}
                                            </span>
                                        </td>
                                        <td style={{ color: '#94a3b8' }}>{plot.last_checked}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Reports

import { useState } from 'react'

function APIPortal() {
    const [apiKey, setApiKey] = useState(null)
    const [loading, setLoading] = useState(false)
    const [department, setDepartment] = useState('Revenue Department')

    const generateKey = () => {
        setLoading(true)
        // Simulate API call
        setTimeout(() => {
            const randomKey = 'csidc_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
            setApiKey(randomKey.toUpperCase())
            setLoading(false)
        }, 1500)
    }

    const copyToClipboard = () => {
        navigator.clipboard.writeText(apiKey)
        alert("API Key copied to clipboard!")
    }

    return (
        <div className="api-portal fade-in">
            <div className="page-header">
                <h2>🔌 Developer API Portal</h2>
                <p>Secure data integration for Government Departments (G2G Interface)</p>
            </div>

            {/* System Health Banner */}
            <div className="glass-card" style={{ marginBottom: 32, padding: '20px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'linear-gradient(90deg, #0f172a 0%, #1e293b 100%)', border: '1px solid #334155' }}>
                <div style={{ display: 'flex', gap: 40 }}>
                    <div>
                        <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>SYSTEM STATUS</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 10px #22c55e' }}></span>
                            <span style={{ fontWeight: 700, color: '#f8fafc' }}>OPERATIONAL</span>
                        </div>
                    </div>
                    <div>
                        <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>API LATENCY</div>
                        <div style={{ fontWeight: 700, color: '#60a5fa' }}>42 ms</div>
                    </div>
                    <div>
                        <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>ACTIVE NODES</div>
                        <div style={{ fontWeight: 700, color: '#f8fafc' }}>CSIDC-HQ-01</div>
                    </div>
                </div>
                <div>
                    <div style={{ fontSize: 12, color: '#94a3b8', textAlign: 'right', marginBottom: 4 }}>TOTAL REQUESTS (24H)</div>
                    <div style={{ fontWeight: 700, fontSize: 20, textAlign: 'right' }}>1.2M</div>
                </div>
            </div>

            <div className="admin-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32 }}>

                {/* Left: Key Generation */}
                <div>
                    <div className="glass-card" style={{ padding: 32 }}>
                        <h3>🔑 Access Management</h3>
                        <p style={{ color: '#94a3b8', marginBottom: 24 }}>
                            Generate secure credentials for your department's applications to access the Land Sentinel Grid.
                        </p>

                        <div className="form-group">
                            <label>Department Name</label>
                            <select
                                className="form-input"
                                value={department}
                                onChange={(e) => setDepartment(e.target.value)}
                            >
                                <option>Revenue Department</option>
                                <option>Electricity Board (CSPDCL)</option>
                                <option>Water Resources (WRD)</option>
                                <option>Town & Country Planning</option>
                                <option>Police Department</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Access Scope</label>
                            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 8 }}>
                                {['read:plots', 'read:violations', 'read:compliance'].map(scope => (
                                    <span key={scope} style={{ background: '#1e293b', padding: '4px 12px', borderRadius: 16, fontSize: 12, color: '#60a5fa', border: '1px solid #3b82f6' }}>
                                        {scope}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {!apiKey ? (
                            <button
                                onClick={generateKey}
                                className="btn-primary"
                                style={{ width: '100%', marginTop: 24 }}
                                disabled={loading}
                            >
                                {loading ? 'Generating Secrets...' : 'Generate API Key'}
                            </button>
                        ) : (
                            <div style={{ marginTop: 24, background: '#0f172a', padding: 16, borderRadius: 8, border: '1px solid #22c55e' }}>
                                <label style={{ color: '#22c55e', fontSize: 12, fontWeight: 700 }}>ACTIVE API KEY</label>
                                <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                                    <code style={{ flex: 1, background: '#1e293b', padding: 8, borderRadius: 4, fontFamily: 'monospace', color: '#e2e8f0' }}>
                                        {apiKey}
                                    </code>
                                    <button
                                        onClick={copyToClipboard}
                                        className="btn-secondary"
                                        style={{ padding: '4px 12px' }}
                                    >
                                        Copy
                                    </button>
                                </div>
                                <p style={{ fontSize: 11, color: '#64748b', marginTop: 12 }}>
                                    ⚠️ Keep this key secure. It grants read access to sensitive land records.
                                </p>
                            </div>
                        )}
                    </div>

                    <div className="glass-card" style={{ marginTop: 24, padding: 24, borderLeft: '4px solid #f59e0b' }}>
                        <div style={{ display: 'flex', gap: 16 }}>
                            <div style={{ fontSize: 24 }}>⚡</div>
                            <div>
                                <h4 style={{ margin: 0, color: '#f59e0b' }}>Rate Limits</h4>
                                <p style={{ fontSize: 13, color: '#94a3b8', margin: '4px 0 0 0' }}>
                                    Standard tier allows 1,000 requests/hour.
                                    <br />For higher limits, contact the CSIDC IT Cell.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right: Documentation */}
                <div>
                    <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
                        <div style={{ padding: '16px 24px', background: '#0f172a', borderBottom: '1px solid #1e293b' }}>
                            <h3 style={{ margin: 0, fontSize: 16 }}>Documentation & Integration</h3>
                        </div>

                        <div style={{ padding: 24 }}>
                            <div style={{ marginBottom: 24 }}>
                                <h4 style={{ color: '#60a5fa', marginBottom: 12 }}>GET /api/plots/{'{id}'}</h4>
                                <p style={{ fontSize: 13, color: '#cbd5e1' }}>Fetch real-time status and compliance score for a specific industrial plot.</p>

                                <div style={{ position: 'relative', marginTop: 12 }}>
                                    <div style={{ position: 'absolute', top: 0, right: 0, background: '#3b82f6', color: 'white', fontSize: 10, padding: '2px 8px', borderRadius: '0 4px 0 4px' }}>PYTHON</div>
                                    <pre style={{ background: '#0f172a', padding: 16, borderRadius: 8, fontSize: 12, overflowX: 'auto', border: '1px solid #1e293b' }}>
                                        {`import requests

url = "https://semt-csidc.gov.in/api/v1/plots/PLOT-402"
headers = {
    "Authorization": "Bearer ${apiKey || 'YOUR_API_KEY'}"
}

response = requests.get(url, headers=headers)
data = response.json()

if data['status'] == 'violation':
    trigger_revenue_alert(data)`}
                                    </pre>
                                </div>
                            </div>

                            <div>
                                <h4 style={{ color: '#60a5fa', marginBottom: 12 }}>GET /api/violations/recent</h4>
                                <p style={{ fontSize: 13, color: '#cbd5e1' }}>Stream latest high-priority encroachments for immediate action.</p>

                                <div style={{ position: 'relative', marginTop: 12 }}>
                                    <div style={{ position: 'absolute', top: 0, right: 0, background: '#f59e0b', color: 'black', fontSize: 10, padding: '2px 8px', borderRadius: '0 4px 0 4px' }}>CURL</div>
                                    <pre style={{ background: '#0f172a', padding: 16, borderRadius: 8, fontSize: 12, overflowX: 'auto', border: '1px solid #1e293b' }}>
                                        {`curl -X GET "https://semt-csidc.gov.in/api/v1/violations" \\
     -H "Authorization: Bearer ${apiKey || 'YOUR_API_KEY'}"`}
                                    </pre>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    )
}

export default APIPortal

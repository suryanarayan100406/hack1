import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet'
import { getApiUrl } from '../config'

function LocationMarker({ setPos }) {
    useMapEvents({
        click(e) {
            setPos(e.latlng)
        },
    })
    return null
}

function CitizenWatch() {
    const [reports, setReports] = useState([])
    const [activeTab, setActiveTab] = useState('map') // map | report
    const [newReportPos, setNewReportPos] = useState(null)
    const [description, setDescription] = useState('')
    const [file, setFile] = useState(null)
    const [submitting, setSubmitting] = useState(false)
    const [message, setMessage] = useState(null)

    useEffect(() => {
        loadReports()
    }, [])

    const loadReports = async () => {
        try {
            const res = await fetch(getApiUrl('/api/citizen/reports'))
            const data = await res.json()
            setReports(data)
        } catch (err) {
            console.error(err)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!newReportPos || !description) return

        setSubmitting(true)
        const formData = new FormData()
        formData.append('description', description)
        formData.append('lat', newReportPos.lat)
        formData.append('lng', newReportPos.lng)
        if (file) formData.append('file', file)

        try {
            const res = await fetch(getApiUrl('/api/citizen/report'), { method: 'POST', body: formData })
            if (res.ok) {
                setMessage({ type: 'success', text: 'Report submitted! Thank you for being a vigilance sentinel.' })
                setNewReportPos(null)
                setDescription('')
                setFile(null)
                loadReports()
                setTimeout(() => setActiveTab('map'), 1500)
            } else {
                setMessage({ type: 'error', text: 'Failed to submit report.' })
            }
        } catch (err) {
            setMessage({ type: 'error', text: 'Network error.' })
        }
        setSubmitting(false)
    }

    return (
        <div>
            <div className="page-header">
                <h2>👁️ Citizen Watch Portal</h2>
                <p>Public vigilance platform for reporting industrial encroachments</p>
            </div>

            <div className="citizen-container" style={{ marginTop: 24, display: 'grid', gridTemplateColumns: '300px 1fr', gap: 24 }}>

                {/* Sidebar */}
                <div className="glass-card" style={{ height: 'fit-content' }}>
                    <div className="map-controls dev-portal-nav" style={{ flexDirection: 'column', gap: 8, marginBottom: 24 }}>
                        <button
                            className={`dev-nav-btn ${activeTab === 'map' ? 'active' : ''}`}
                            onClick={() => setActiveTab('map')}
                        >
                            🌍 View Reports
                        </button>
                        <button
                            className={`dev-nav-btn ${activeTab === 'report' ? 'active' : ''}`}
                            onClick={() => setActiveTab('report')}
                        >
                            📢 Report Violation
                        </button>
                    </div>

                    <div style={{ padding: 12, background: 'rgba(30, 41, 59, 0.5)', borderRadius: 8 }}>
                        <h4 style={{ margin: '0 0 12px 0', fontSize: 14 }}>Recent Reports</h4>
                        {reports.map((r, i) => (
                            <div key={i} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: '1px solid #334155' }}>
                                <div style={{ fontSize: 13, fontWeight: 600 }}>{r.description}</div>
                                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
                                    {new Date(r.timestamp).toLocaleDateString()} •
                                    <span style={{ color: r.status === 'pending' ? '#f59e0b' : '#10b981', marginLeft: 4 }}>
                                        {r.status.toUpperCase()}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Main Content */}
                <div className="glass-card" style={{ padding: 0, overflow: 'hidden', minHeight: 500, display: 'flex', flexDirection: 'column' }}>

                    {activeTab === 'map' && (
                        <div style={{ flex: 1, position: 'relative' }}>
                            <MapContainer center={[21.2800, 81.5700]} zoom={14} style={{ height: '100%', width: '100%' }}>
                                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

                                {reports.map((r, i) => (
                                    <Marker key={i} position={[r.lat, r.lng]}>
                                        <Popup>
                                            <strong>{r.description}</strong><br />
                                            Status: {r.status}
                                        </Popup>
                                    </Marker>
                                ))}
                            </MapContainer>
                            <div style={{ position: 'absolute', top: 10, right: 10, timeout: 1000, background: 'rgba(0,0,0,0.7)', padding: 10, borderRadius: 8, zIndex: 1000, fontSize: 12 }}>
                                🟢 Resolved &nbsp; 🟠 Pending
                            </div>
                        </div>
                    )}

                    {activeTab === 'report' && (
                        <div style={{ padding: 32, maxWidth: 600, margin: '0 auto', width: '100%' }}>
                            <h3 style={{ marginBottom: 24 }}>Submit New Report</h3>

                            {message && (
                                <div className={`alert ${message.type === 'error' ? 'alert-danger' : 'alert-success'}`} style={{ marginBottom: 20 }}>
                                    {message.text}
                                </div>
                            )}

                            <form onSubmit={handleSubmit}>
                                <div className="form-group">
                                    <label>Description</label>
                                    <textarea
                                        className="form-input"
                                        rows={4}
                                        value={description}
                                        onChange={e => setDescription(e.target.value)}
                                        placeholder="Describe the encroachment or violation..."
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Location (Click on map to set)</label>
                                    <div style={{ height: 200, borderRadius: 8, overflow: 'hidden', border: '1px solid #334155', marginBottom: 8 }}>
                                        <MapContainer center={[21.2800, 81.5700]} zoom={13} style={{ height: '100%', width: '100%' }}>
                                            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                                            <LocationMarker setPos={setNewReportPos} />
                                            {newReportPos && <Marker position={newReportPos} />}
                                        </MapContainer>
                                    </div>
                                    {newReportPos ? (
                                        <div style={{ fontSize: 12, color: '#22c55e' }}>✅ Location set: {newReportPos.lat.toFixed(5)}, {newReportPos.lng.toFixed(5)}</div>
                                    ) : (
                                        <div style={{ fontSize: 12, color: '#ef4444' }}>⚠️ Please click on the map above to pin the location</div>
                                    )}
                                </div>

                                <div className="form-group">
                                    <label>Evidence (Photo)</label>
                                    <input type="file" onChange={e => setFile(e.target.files[0])} className="form-input" accept="image/*" />
                                </div>

                                <button
                                    type="submit"
                                    className="btn-primary"
                                    style={{ width: '100%', marginTop: 16 }}
                                    disabled={submitting || !newReportPos || !description}
                                >
                                    {submitting ? 'Submitting...' : '🚀 Submit Report'}
                                </button>
                            </form>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default CitizenWatch

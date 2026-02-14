import { useState } from 'react'
import { getApiUrl } from '../config'

function AdminPanel({ onNavigate }) {
    const [file, setFile] = useState(null)
    const [preview, setPreview] = useState(null)
    const [vectorPreview, setVectorPreview] = useState(null)
    const [plotsPreview, setPlotsPreview] = useState(null)
    const [plotCount, setPlotCount] = useState(0)

    // Metadata
    const [id, setId] = useState('')
    const [name, setName] = useState('')
    const [category, setCategory] = useState('Industrial Area')
    const [area, setArea] = useState('')

    // Geo Bounds (Default to Urla approx for ease)
    const [latMin, setLatMin] = useState('21.2750')
    const [latMax, setLatMax] = useState('21.2950')
    const [lngMin, setLngMin] = useState('81.5650')
    const [lngMax, setLngMax] = useState('81.5850')

    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState(null)

    const handleFile = (e) => {
        const selected = e.target.files[0]
        if (selected) {
            setFile(selected)
            setPreview(URL.createObjectURL(selected))
            setVectorPreview(null)
            setMessage({ type: 'info', text: 'Map loaded. Please fill details.' })
        }
    }

    const handleExtractPlots = async () => {
        if (!file) return
        setLoading(true)
        setMessage({ type: 'info', text: '🤖 AI detecting plots...' })

        const formData = new FormData()
        formData.append('file', file)

        try {
            const res = await fetch(getApiUrl('/api/admin/vectorize-plots'), { method: 'POST', body: formData })
            if (!res.ok) throw new Error(await res.text())
            const data = await res.json()
            setPlotsPreview(data.preview_image)
            setPlotCount(data.count)
            setMessage({ type: 'success', text: `Found ${data.count} plots! AI Mapping Complete.` })
        } catch (err) {
            console.error(err)
            setMessage({ type: 'error', text: 'Plot detection failed' })
        }
        setLoading(false)
    }

    const handleDigitize = async () => {
        if (!file) return
        setLoading(true)
        setMessage(null)
        setPlotsPreview(null) // Reset plots if digitizing full layout

        const formData = new FormData()
        formData.append('file', file)

        try {
            const res = await fetch(getApiUrl('/api/admin/digitize'), { method: 'POST', body: formData })
            if (!res.ok) throw new Error(await res.text())
            const data = await res.json()
            setVectorPreview(data.preview_image) // Base64 image with overlay
            setMessage({ type: 'success', text: `Vectorization Complete! Area: ${Math.round(data.area_px)} px` })
        } catch (err) {
            console.error(err)
            setMessage({ type: 'error', text: 'Digitization failed' })
        }
        setLoading(false)
    }

    const handleSave = async () => {
        if (!file || !id || !name) return

        // Validation: Check for "Dot" coordinates
        const laMin = parseFloat(latMin)
        const laMax = parseFloat(latMax)
        const loMin = parseFloat(lngMin)
        const loMax = parseFloat(lngMax)

        if (Math.abs(laMax - laMin) < 0.0001 || Math.abs(loMax - loMin) < 0.0001) {
            setMessage({ type: 'error', text: 'Error: Coordinates are too close! (Result would be a dot). Check Min/Max values.' })
            return
        }
        if (laMin >= laMax || loMin >= loMax) {
            setMessage({ type: 'error', text: 'Error: Min values must be less than Max values.' })
            return
        }

        setLoading(true)

        const formData = new FormData()
        formData.append('file', file)
        formData.append('id', id)
        formData.append('name', name)
        formData.append('category', category)
        formData.append('approved_area', area || 0)
        formData.append('lat_min', latMin)
        formData.append('lat_max', latMax)
        formData.append('lng_min', lngMin)
        formData.append('lng_max', lngMax)

        try {
            const res = await fetch(getApiUrl('/api/admin/upload-layout'), { method: 'POST', body: formData })
            if (!res.ok) throw new Error(await res.text())
            setMessage({ type: 'success', text: 'Layout saved to Registry successfully!' })

            // Clear form
            setFile(null)
            setPreview(null)
            setVectorPreview(null)
            setId('')
            setName('')
        } catch (err) {
            console.error(err)
            setMessage({ type: 'error', text: 'Upload failed' })
        }
        setLoading(false)
    }

    return (
        <div className="upload-page">
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2>🗺️ Admin Map Digitization</h2>
                    <p>Upload official government maps or import from CSIDC GIS</p>
                </div>
                <button onClick={() => onNavigate('dashboard')} className="btn-secondary">
                    ← Back to Analysis
                </button>
            </div>

            {/* Tabs Removed - Direct Upload Mode */}

            <div className="admin-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, marginTop: 24 }}>

                {/* Left Column: Source Selection */}
                <div>
                    <div className="glass-card" style={{ padding: 24 }}>
                        {preview ? (
                            <>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                                    <h3 style={{ margin: 0 }}>1. Preview & Verify</h3>
                                    <button
                                        onClick={() => document.getElementById('file-upload').click()}
                                        className="btn-secondary"
                                        style={{ padding: '4px 8px', fontSize: 12 }}
                                    >
                                        Change Image
                                    </button>
                                </div>
                                <div
                                    style={{ position: 'relative', borderRadius: 8, overflow: 'hidden', border: '2px solid #3b82f6', cursor: 'crosshair' }}
                                    onDoubleClick={(e) => {
                                        const rect = e.target.getBoundingClientRect();
                                        const x = e.clientX - rect.left;
                                        const y = e.clientY - rect.top;

                                        // Interpolate
                                        const lat = parseFloat(latMax) - (y / rect.height) * (parseFloat(latMax) - parseFloat(latMin));
                                        const lng = parseFloat(lngMin) + (x / rect.width) * (parseFloat(lngMax) - parseFloat(lngMin));

                                        window.open(`https://www.google.com/maps/search/?api=1&query=${lat},${lng}`, '_blank');
                                        setMessage({ type: 'info', text: `Opened Google Maps at ${lat.toFixed(5)}, ${lng.toFixed(5)}` });
                                    }}
                                    title="Double-click any point to verify on Google Maps"
                                >
                                    <img src={preview} alt="Preview" style={{ width: '100%', display: 'block' }} />
                                    <div style={{ position: 'absolute', bottom: 8, right: 8, background: 'rgba(0,0,0,0.7)', color: 'white', padding: '4px 8px', borderRadius: 4, fontSize: 10, pointerEvents: 'none' }}>
                                        Double-click to Verify ↗
                                    </div>
                                </div>
                            </>
                        ) : (
                            <>
                                <h3 onClick={() => document.getElementById('file-upload').click()} style={{ cursor: 'pointer', marginBottom: 16 }}>
                                    1. Upload Map Image
                                </h3>
                                <div
                                    className="upload-zone"
                                    style={{ padding: 40, borderStyle: 'dashed' }}
                                    onClick={() => document.getElementById('file-upload').click()}
                                >
                                    <div>
                                        <div style={{ fontSize: 32 }}>📁</div>
                                        <p>Click to upload PNG/JPG</p>
                                    </div>
                                </div>
                            </>
                        )}
                        <input id="file-upload" type="file" hidden accept="image/*" onChange={handleFile} />

                        {/* Metadata Inputs (Shared) */}
                        <div className="form-group" style={{ marginTop: 24 }}>
                            <label>Industrial Area ID</label>
                            <input className="form-input" value={id} onChange={e => setId(e.target.value)} placeholder="e.g. URLA-ZONE-4" />
                        </div>
                        <div className="form-group">
                            <label>Official Name</label>
                            <input className="form-input" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Urla Expansion Zone" />
                        </div>
                        <div className="form-group">
                            <label>Category</label>
                            <select className="form-input" value={category} onChange={e => setCategory(e.target.value)}>
                                <option>Industrial Area</option>
                                <option>Growth Center</option>
                                <option>IT Park</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Total Area (sqm)</label>
                            <input className="form-input" type="number" value={area} onChange={e => setArea(e.target.value)} />
                        </div>
                    </div>

                    {/* Geo-Referencing */}
                    <div className="glass-card" style={{ padding: 24, marginTop: 24 }}>
                        <h3>2. Geo-Referencing</h3>
                        <p style={{ fontSize: 12, color: '#94a3b8', marginBottom: 16 }}>Enter the Lat/Lng bounding box for this map image.</p>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                            <div>
                                <label style={{ fontSize: 12 }}>Min Latitude</label>
                                <input type="number" step="0.000001" className="form-input" value={latMin} onChange={e => setLatMin(e.target.value)} />
                            </div>
                            <div>
                                <label style={{ fontSize: 12 }}>Max Latitude</label>
                                <input type="number" step="0.000001" className="form-input" value={latMax} onChange={e => setLatMax(e.target.value)} />
                            </div>
                            <div>
                                <label style={{ fontSize: 12 }}>Min Longitude</label>
                                <input type="number" step="0.000001" className="form-input" value={lngMin} onChange={e => setLngMin(e.target.value)} />
                            </div>
                            <div>
                                <label style={{ fontSize: 12 }}>Max Longitude</label>
                                <input type="number" step="0.000001" className="form-input" value={lngMax} onChange={e => setLngMax(e.target.value)} />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Column: Preview */}
                <div>
                    <div className="glass-card" style={{ padding: 24, height: '100%' }}>
                        <h3>3. Digital Twin Preview</h3>

                        <div style={{ margin: '24px 0', minHeight: 300, background: '#0f172a', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            {loading ? (
                                <div className="spinner">⚙️ Processing...</div>
                            ) : plotsPreview ? (
                                <div style={{ position: 'relative', width: '100%' }}>
                                    <img src={plotsPreview} alt="Plots Overlay" style={{ width: '100%', borderRadius: 8, border: '2px solid #3b82f6' }} />
                                    <div style={{ position: 'absolute', bottom: 10, left: 10, background: 'rgba(0,0,0,0.7)', padding: '4px 8px', borderRadius: 4, fontSize: 12, color: '#60a5fa' }}>
                                        🏙️ {plotCount} Plots Detected
                                    </div>
                                </div>
                            ) : vectorPreview ? (
                                <div style={{ position: 'relative', width: '100%' }}>
                                    <img src={vectorPreview} alt="Vector Overlay" style={{ width: '100%', borderRadius: 8, border: '2px solid #22c55e' }} />
                                    <div style={{ position: 'absolute', bottom: 10, left: 10, background: 'rgba(0,0,0,0.7)', padding: '4px 8px', borderRadius: 4, fontSize: 12, color: '#4ade80' }}>
                                        ✅ Layout Digitized
                                    </div>
                                </div>
                            ) : (
                                <p style={{ color: '#64748b' }}>Vector preview will appear here</p>
                            )}
                        </div>

                        {message && (
                            <div className={`alert ${message.type === 'error' ? 'alert-danger' : 'alert-success'}`} style={{ marginBottom: 16, padding: 12, borderRadius: 6, background: message.type === 'error' ? '#ef444420' : '#22c55e20', color: message.type === 'error' ? '#f87171' : '#4ade80' }}>
                                {message.text}
                            </div>
                        )}

                        <div style={{ display: 'flex', gap: 12 }}>
                            <button
                                className="btn-secondary"
                                style={{ flex: 1, background: '#0f172a', border: '1px solid #3b82f6', color: '#60a5fa' }}
                                onClick={handleExtractPlots}
                                disabled={!file || loading}
                            >
                                🏙️ Extract Plots
                            </button>
                            <button
                                className="btn-secondary"
                                style={{ flex: 1 }}
                                onClick={handleDigitize}
                                disabled={!file || loading}
                            >
                                ⚡ Boundary
                            </button>
                            <button
                                className="btn-primary"
                                style={{ flex: 1 }}
                                onClick={handleSave}
                                disabled={!file || !id || loading}
                            >
                                💾 Save
                            </button>
                        </div>

                        <div style={{ marginTop: 20, fontSize: 13, color: '#94a3b8' }}>
                            <p><strong>Note:</strong> "Extract Plots" uses AI to auto-detect sub-plots. "Boundary" finds the outer perimeter. Save to commit to Registry.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AdminPanel

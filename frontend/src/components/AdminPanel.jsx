import { useState } from 'react'

function AdminPanel({ onNavigate }) {
    const [file, setFile] = useState(null)
    const [preview, setPreview] = useState(null)
    const [vectorPreview, setVectorPreview] = useState(null)

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

    const [activeTab, setActiveTab] = useState('upload') // 'upload' or 'gis'

    const handleFile = async (e) => {
        const selected = e.target.files[0]
        if (selected) {
            setFile(selected)
            setPreview(URL.createObjectURL(selected))
            setVectorPreview(null)

            // AI Autofill Trigger
            setMessage({ type: 'info', text: '✨ AI Analyzing map text...' })

            const formData = new FormData()
            formData.append('file', selected)

            try {
                const res = await fetch('/api/admin/analyze-layout', { method: 'POST', body: formData })
                if (res.ok) {
                    const { data } = await res.json()

                    if (data.name) setName(data.name)
                    if (data.area) setArea(data.area)
                    if (data.id) setId(data.id)

                    const found = []
                    if (data.name) found.push("Name")
                    if (data.area) found.push("Area")
                    if (data.id) found.push("ID")

                    if (found.length > 0) {
                        setMessage({ type: 'success', text: `✨ AI Autocomplete: Found ${found.join(', ')}` })
                    } else {
                        setMessage({ type: 'info', text: 'Map loaded. Please fill details.' })
                    }
                }
            } catch (err) {
                console.error("AI Analysis failed", err)
                // Silent fail, user can type manually
            }
        }
    }

    const handleDigitize = async () => {
        if (!file) return
        setLoading(true)
        setMessage(null)

        const formData = new FormData()
        formData.append('file', file)

        try {
            const res = await fetch('/api/admin/digitize', { method: 'POST', body: formData })
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
            const res = await fetch('/api/admin/upload-layout', { method: 'POST', body: formData })
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

            {/* Tabs */}
            <div style={{ display: 'flex', gap: 16, marginTop: 24, paddingBottom: 12, borderBottom: '1px solid #334155' }}>
                <button
                    className={`btn-tab ${activeTab === 'upload' ? 'active' : ''}`}
                    style={{ background: activeTab === 'upload' ? '#3b82f6' : 'transparent', border: 'none', padding: '8px 16px', borderRadius: 6, color: 'white', cursor: 'pointer' }}
                    onClick={() => setActiveTab('upload')}
                >
                    📁 Upload Image
                </button>
                <button
                    className={`btn-tab ${activeTab === 'gis' ? 'active' : ''}`}
                    style={{ background: activeTab === 'gis' ? '#3b82f6' : 'transparent', border: 'none', padding: '8px 16px', borderRadius: 6, color: 'white', cursor: 'pointer' }}
                    onClick={() => setActiveTab('gis')}
                >
                    🌏 Official GIS (CSIDC)
                </button>
            </div>

            <div className="admin-grid" style={{ display: 'grid', gridTemplateColumns: activeTab === 'gis' ? '1fr' : '1fr 1fr', gap: 32, marginTop: 24 }}>

                {/* GIS Mode: Full Screen Experience */}
                {activeTab === 'gis' ? (
                    <div className="glass-card" style={{ padding: 16, height: '80vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

                        {/* Header Controls */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                            <div>
                                <h3 style={{ margin: 0 }}>🌏 Official CSIDC Map Portal</h3>
                                <p style={{ margin: 0, fontSize: 12, color: '#94a3b8' }}>
                                    Navigate to your area → Use map's <strong>Export</strong> tool (PNG/JPG) → Upload below.
                                </p>
                            </div>
                            <div style={{ display: 'flex', gap: 12 }}>
                                <a href="https://cggis.cgstate.gov.in/csidc/" target="_blank" rel="noopener noreferrer" className="btn-secondary" style={{ textDecoration: 'none', padding: '6px 12px', fontSize: 13 }}>
                                    Open in New Tab ↗
                                </a>
                                <button
                                    className="btn-primary"
                                    onClick={() => document.getElementById('file-upload-export').click()}
                                    style={{ background: '#22c55e' }}
                                >
                                    📥 Upload Exported Map
                                </button>
                                <input
                                    id="file-upload-export"
                                    type="file"
                                    hidden
                                    accept="image/*"
                                    onChange={(e) => {
                                        handleFile(e);
                                        setActiveTab('upload'); // Switch to editor view
                                        setMessage({ type: 'info', text: 'Map loaded! Please enter details & confirm geo-box.' });
                                    }}
                                />
                            </div>
                        </div>

                        {/* Maximize Iframe */}
                        <div style={{ flex: 1, background: '#fff', borderRadius: 8, overflow: 'hidden', border: '2px solid #334155', position: 'relative' }}>
                            <iframe
                                src="https://cggis.cgstate.gov.in/csidc/"
                                style={{ width: '100%', height: '100%', border: 'none' }}
                                title="CSIDC GIS"
                            ></iframe>
                        </div>
                    </div>
                ) : (
                    /* Default Upload View (Split Columns) */
                    <>
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
                                                // Lat decreases as Y increases (Top is Max, Bottom is Min)
                                                const lat = parseFloat(latMax) - (y / rect.height) * (parseFloat(latMax) - parseFloat(latMin));
                                                // Lng increases as X increases (Left is Min, Right is Max)
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
                            {activeTab === 'upload' && (
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
                            )}
                        </div>
                    </>
                )}

                {activeTab === 'upload' && (
                    <div>
                        <div className="glass-card" style={{ padding: 24, height: '100%' }}>
                            <h3>3. Digital Twin Preview</h3>

                            <div style={{ margin: '24px 0', minHeight: 300, background: '#0f172a', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                {loading ? (
                                    <div className="spinner">⚙️ Processing...</div>
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
                                    style={{ flex: 1 }}
                                    onClick={handleDigitize}
                                    disabled={!file || loading}
                                >
                                    ⚡ Preview Vector
                                </button>
                                <button
                                    className="btn-primary"
                                    style={{ flex: 1 }}
                                    onClick={handleSave}
                                    disabled={!file || !id || loading}
                                >
                                    💾 Save to Registry
                                </button>
                            </div>

                            <div style={{ marginTop: 20, fontSize: 13, color: '#94a3b8' }}>
                                <p><strong>Note:</strong> "Preview Vector" extracts the polygon boundary using computer vision. "Save to Registry" will commit this polygon to the database with the geocoordinates provided.</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default AdminPanel

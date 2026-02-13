import { useState, useRef } from 'react'

function Upload({ onNavigate }) {
    const [refImage, setRefImage] = useState(null)
    const [satImage, setSatImage] = useState(null)
    const [refPreview, setRefPreview] = useState(null)
    const [satPreview, setSatPreview] = useState(null)
    const [projectName, setProjectName] = useState('')
    const [uploading, setUploading] = useState(false)
    const [result, setResult] = useState(null)
    const [dragOver, setDragOver] = useState(null)
    const refInput = useRef(null)
    const satInput = useRef(null)

    const handleFile = (file, type) => {
        if (!file) return
        const reader = new FileReader()
        reader.onload = (e) => {
            if (type === 'ref') {
                setRefImage(file)
                setRefPreview(e.target.result)
            } else {
                setSatImage(file)
                setSatPreview(e.target.result)
            }
        }
        reader.readAsDataURL(file)
    }

    const handleDrop = (e, type) => {
        e.preventDefault()
        setDragOver(null)
        const file = e.dataTransfer.files[0]
        if (file && file.type.startsWith('image/')) {
            handleFile(file, type)
        }
    }

    const handleSubmit = async () => {
        if (!refImage || !satImage) return
        setUploading(true)
        setResult(null)

        try {
            const formData = new FormData()
            formData.append('reference', refImage)
            formData.append('satellite', satImage)
            if (projectName) formData.append('project_name', projectName)

            const uploadRes = await fetch('/api/upload', { method: 'POST', body: formData })
            const uploadData = await uploadRes.json()

            if (uploadData.project?.id) {
                const analyzeRes = await fetch(`/api/analyze/${uploadData.project.id}`, { method: 'POST' })
                const analyzeData = await analyzeRes.json()
                setResult(analyzeData)
            }
        } catch (err) {
            setResult({ error: 'Analysis failed. Please try again.' })
        }

        setUploading(false)
    }

    return (
        <div>
            <div className="page-header">
                <h2>📤 Upload & Analyze</h2>
                <p>Upload a reference allotment map and a satellite/drone image to detect changes</p>
            </div>

            <div className="upload-page" style={{ marginTop: 24 }}>
                {/* Project Name */}
                <div style={{ marginBottom: 20 }}>
                    <label className="form-label">Project Name (optional)</label>
                    <input
                        type="text"
                        className="form-input"
                        placeholder="e.g., Urla Zone-3 February Scan"
                        value={projectName}
                        onChange={(e) => setProjectName(e.target.value)}
                        style={{ maxWidth: 400 }}
                    />
                </div>

                {/* Upload Zones */}
                <div className="upload-preview">
                    {/* Reference Map */}
                    <div className="preview-card">
                        <div
                            className={`upload-zone ${dragOver === 'ref' ? 'drag-over' : ''}`}
                            onClick={() => refInput.current?.click()}
                            onDragOver={(e) => { e.preventDefault(); setDragOver('ref') }}
                            onDragLeave={() => setDragOver(null)}
                            onDrop={(e) => handleDrop(e, 'ref')}
                            style={{ padding: refPreview ? '16px' : '48px' }}
                        >
                            {refPreview ? (
                                <img src={refPreview} alt="Reference Map" style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 8 }} />
                            ) : (
                                <>
                                    <div className="upload-icon">🗺️</div>
                                    <h3>Reference Map</h3>
                                    <p>Drop the original allotment map here or click to browse</p>
                                </>
                            )}
                        </div>
                        <input
                            type="file"
                            ref={refInput}
                            style={{ display: 'none' }}
                            accept="image/*"
                            onChange={(e) => handleFile(e.target.files[0], 'ref')}
                        />
                        <div className="label" style={{ marginTop: 8 }}>📌 Reference / Allotment Map</div>
                    </div>

                    {/* Satellite Image */}
                    <div className="preview-card">
                        <div
                            className={`upload-zone ${dragOver === 'sat' ? 'drag-over' : ''}`}
                            onClick={() => satInput.current?.click()}
                            onDragOver={(e) => { e.preventDefault(); setDragOver('sat') }}
                            onDragLeave={() => setDragOver(null)}
                            onDrop={(e) => handleDrop(e, 'sat')}
                            style={{ padding: satPreview ? '16px' : '48px' }}
                        >
                            {satPreview ? (
                                <img src={satPreview} alt="Satellite Image" style={{ maxWidth: '100%', maxHeight: 200, borderRadius: 8 }} />
                            ) : (
                                <>
                                    <div className="upload-icon">🛰️</div>
                                    <h3>Current Image</h3>
                                    <p>Drop the latest satellite or drone image here or click to browse</p>
                                </>
                            )}
                        </div>
                        <input
                            type="file"
                            ref={satInput}
                            style={{ display: 'none' }}
                            accept="image/*"
                            onChange={(e) => handleFile(e.target.files[0], 'sat')}
                        />
                        <div className="label" style={{ marginTop: 8 }}>🛰️ Satellite / Drone Image</div>
                    </div>
                </div>

                {/* Analyze Button */}
                <div style={{ textAlign: 'center', marginTop: 24 }}>
                    <button
                        className="btn-primary"
                        disabled={!refImage || !satImage || uploading}
                        onClick={handleSubmit}
                    >
                        {uploading ? '⏳ Analyzing...' : '🔍 Run Change Detection'}
                    </button>
                </div>

                {/* Results */}
                {result && !result.error && (
                    <div className="animate-in" style={{ marginTop: 32 }}>
                        <h3 style={{ marginBottom: 16, fontSize: 18 }}>📊 Analysis Results</h3>

                        {/* Summary KPIs */}
                        <div className="kpi-grid" style={{ marginBottom: 20 }}>
                            <div className={`kpi-card ${result.change_detection.severity === 'low' ? 'success' : result.change_detection.severity === 'critical' ? 'danger' : 'warning'}`}>
                                <div className="kpi-header">
                                    <span className="kpi-label">Encroachment</span>
                                </div>
                                <div className="kpi-value">{result.change_detection.change_percentage}%</div>
                                <div className="kpi-sub">of allotted boundary</div>
                            </div>
                            <div className="kpi-card info">
                                <div className="kpi-header">
                                    <span className="kpi-label">Deviation Zones</span>
                                </div>
                                <div className="kpi-value">{result.change_detection.num_change_regions}</div>
                                <div className="kpi-sub">structural deviations</div>
                            </div>
                            <div className="kpi-card primary">
                                <div className="kpi-header">
                                    <span className="kpi-label">Compliance Score</span>
                                </div>
                                <div className="kpi-value">{result.compliance_score}</div>
                                <div className="kpi-sub">out of 100</div>
                            </div>
                            <div className={`kpi-card ${result.change_detection.status === 'compliant' ? 'success' : 'danger'}`}>
                                <div className="kpi-header">
                                    <span className="kpi-label">Verdict</span>
                                </div>
                                <div className="kpi-value" style={{ fontSize: 22 }}>
                                    <span className={`status-badge ${result.change_detection.status}`}>
                                        {result.change_detection.status.replace(/_/g, ' ')}
                                    </span>
                                </div>
                            </div>
                        </div>
                        {/* Area Analysis Stats */}
                        <div className="glass-card" style={{ marginBottom: 20, padding: 16 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-around', textAlign: 'center' }}>
                                <div>
                                    <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Total Image Pixels</div>
                                    <div style={{ fontSize: 18, fontWeight: 700 }}>{result.change_detection.total_pixels.toLocaleString()}</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Approved Area (px)</div>
                                    <div style={{ fontSize: 18, fontWeight: 700, color: '#22c55e' }}>{result.change_detection.approved_area_px.toLocaleString()}</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Encroached Area (px)</div>
                                    <div style={{ fontSize: 18, fontWeight: 700, color: '#ef4444' }}>
                                        {result.change_detection.changed_pixels.toLocaleString()}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Result Images */}
                        <div className="analysis-grid">
                            <div className="analysis-image-card">
                                <div className="card-header">🔥 Encroachment Heatmap</div>
                                <img src={result.outputs.heatmap} alt="Heatmap" />
                            </div>
                            <div className="analysis-image-card">
                                <div className="card-header">🎯 Approved Boundary (Green)</div>
                                <img src={result.outputs.comparison} alt="Comparison" />
                            </div>
                            <div className="analysis-image-card">
                                <div className="card-header">💀 Encroachment Mask (Binary)</div>
                                <img src={result.outputs.mask} alt="Mask" />
                            </div>
                            <div className="analysis-image-card">
                                <div className="card-header">↔️ Reference vs Satellite</div>
                                <img src={result.outputs.comparison} alt="Comparison" />
                            </div>
                        </div>
                    </div>
                )}

                {result?.error && (
                    <div style={{ textAlign: 'center', marginTop: 24, color: '#ef4444' }}>
                        ❌ {result.error}
                    </div>
                )}

                {/* Instructions */}
                <div className="glass-card" style={{ marginTop: 32 }}>
                    <h3 style={{ marginBottom: 12, fontSize: 16 }}>ℹ️ How it works</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20 }}>
                        {[
                            { icon: '1️⃣', title: 'Upload Images', desc: 'Upload the original allotment/reference map and a recent satellite or drone image of the same area' },
                            { icon: '2️⃣', title: 'Structural Analysis', desc: 'Our engine extracts edges and built-up areas from both images, then compares structural boundaries — not raw pixels' },
                            { icon: '3️⃣', title: 'Encroachment Report', desc: 'View boundary overlays, edge comparisons, encroachment %, and compliance scores based on actual structural deviation' },
                        ].map(step => (
                            <div key={step.title} style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: 28, marginBottom: 8 }}>{step.icon}</div>
                                <h4 style={{ fontSize: 14, marginBottom: 4 }}>{step.title}</h4>
                                <p style={{ fontSize: 12, color: '#94a3b8' }}>{step.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Upload

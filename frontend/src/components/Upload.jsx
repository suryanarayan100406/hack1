import { useState, useRef, useEffect } from 'react'
import { getApiUrl } from '../config'

function Upload({ onNavigate }) {
    const [refImage, setRefImage] = useState(null)
    const [satImage, setSatImage] = useState(null)
    const [refPreview, setRefPreview] = useState(null)
    const [satPreview, setSatPreview] = useState(null)
    const [projectName, setProjectName] = useState('')
    const [uploading, setUploading] = useState(false)
    const [result, setResult] = useState(null)
    const [dragOver, setDragOver] = useState(null)

    // Registry State
    const [uploadMode, setUploadMode] = useState('registry') // 'registry' | 'manual'
    const [layouts, setLayouts] = useState([])
    const [selectedPlotId, setSelectedPlotId] = useState('')

    const refInput = useRef(null)
    const satInput = useRef(null)

    // Load Registry on Mount
    useEffect(() => {
        fetch(getApiUrl('/api/registry'))
            .then(res => res.json())
            .then(data => {
                console.log("Registry Data:", data)
                if (Array.isArray(data)) {
                    setLayouts(data)
                    if (data.length > 0) setSelectedPlotId(data[0].id)
                } else {
                    console.error("Registry data is not an array:", data)
                    setLayouts([])
                }
            })
            .catch(err => {
                console.error("Failed to load registry", err)
                setLayouts([])
            })
    }, [])

    useEffect(() => {
        const preSelected = localStorage.getItem('selected_registry_id')
        if (preSelected) {
            console.log("Found pre-selected plot:", preSelected)
            setSelectedPlotId(preSelected)
            setUploadMode('registry')
            localStorage.removeItem('selected_registry_id')
        }
    }, [layouts]) // Run when layouts loads to ensure ID exists? Actually ID set is independent.

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
        // Validation
        if (!satImage) return
        if (uploadMode === 'manual' && !refImage) return
        if (uploadMode === 'registry' && !selectedPlotId) return

        setUploading(true)
        setResult(null)

        try {
            const formData = new FormData()
            formData.append('satellite', satImage)
            if (projectName) formData.append('project_name', projectName)

            if (uploadMode === 'registry') {
                formData.append('plot_id', selectedPlotId)
            } else {
                formData.append('reference', refImage)
            }


            const uploadRes = await fetch(getApiUrl('/api/upload'), { method: 'POST', body: formData })
            if (!uploadRes.ok) throw new Error(await uploadRes.text())

            const uploadData = await uploadRes.json()

            if (uploadData.project?.id) {
                // 2. Trigger Analysis
                const analyzeRes = await fetch(getApiUrl(`/api/analyze/${uploadData.project.id}`), { method: 'POST' })
                if (!analyzeRes.ok) throw new Error(await analyzeRes.text())
                const analyzeData = await analyzeRes.json()
                setResult(analyzeData)
            }
        } catch (err) {
            console.error(err)
            // Extract error message from JSON if possible
            let msg = 'Analysis failed.'
            try {
                if (err.message.includes('{')) {
                    const parsed = JSON.parse(err.message)
                    msg = parsed.detail || msg
                } else {
                    msg = err.message
                }
            } catch (e) { }
            setResult({ error: msg })
        }

        setUploading(false)
    }

    return (
        <div>
            <div className="page-header">
                <h2>📤 Upload & Analyze</h2>
                <p>Compare satellite imagery against official CSIDC land records.</p>
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

                {/* Mode Switcher */}
                <div className="glass-card" style={{ marginBottom: 24, padding: 4, display: 'inline-flex', gap: 4, background: 'rgba(30, 41, 59, 0.5)' }}>
                    <button
                        onClick={() => setUploadMode('registry')}
                        style={{
                            padding: '8px 16px', borderRadius: 6, border: 'none', cursor: 'pointer',
                            background: uploadMode === 'registry' ? '#3b82f6' : 'transparent',
                            color: uploadMode === 'registry' ? 'white' : '#94a3b8',
                            fontWeight: 600
                        }}
                    >
                        🏛️ Official Registry
                    </button>
                    <button
                        onClick={() => setUploadMode('manual')}
                        style={{
                            padding: '8px 16px', borderRadius: 6, border: 'none', cursor: 'pointer',
                            background: uploadMode === 'manual' ? '#3b82f6' : 'transparent',
                            color: uploadMode === 'manual' ? 'white' : '#94a3b8',
                            fontWeight: 600
                        }}
                    >
                        📤 Manual Upload
                    </button>
                </div>

                {/* Upload Zones */}
                <div className="upload-preview">

                    {/* Reference Map Section */}
                    {uploadMode === 'registry' ? (
                        <div className="preview-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                            <div className="upload-icon">🗺️</div>
                            <h3>Official Land Record</h3>
                            <p style={{ marginBottom: 16 }}>Select a plot from the CSIDC database</p>

                            <div className="registry-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: 12, maxHeight: 400, overflowY: 'auto', padding: 4 }}>
                                {layouts.map(l => (
                                    <div
                                        key={l.id}
                                        onClick={() => setSelectedPlotId(l.id)}
                                        className={`registry-card ${selectedPlotId === l.id ? 'selected' : ''}`}
                                        style={{
                                            padding: 8,
                                            borderRadius: 8,
                                            border: selectedPlotId === l.id ? '2px solid #3b82f6' : '1px solid rgba(255,255,255,0.1)',
                                            background: selectedPlotId === l.id ? 'rgba(59, 130, 246, 0.2)' : 'rgba(30, 41, 59, 0.6)',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s',
                                            textAlign: 'center'
                                        }}
                                    >
                                        <div style={{
                                            height: 80,
                                            marginBottom: 8,
                                            borderRadius: 4,
                                            overflow: 'hidden',
                                            background: '#000',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            {l.thumbnail ? (
                                                <img
                                                    src={getApiUrl(l.thumbnail)}
                                                    alt={l.name}
                                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                    onError={(e) => { e.target.onerror = null; e.target.style.display = 'none' }}
                                                />
                                            ) : (
                                                <span style={{ fontSize: 24 }}>🗺️</span>
                                            )}
                                        </div>
                                        <div style={{ fontSize: 12, fontWeight: 600, color: '#e2e8f0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                            {l.name}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {selectedPlotId && (
                                <div style={{ marginTop: 12, fontSize: 13, color: '#60a5fa', background: 'rgba(59, 130, 246, 0.1)', padding: 8, borderRadius: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <span>✅ Selected: </span>
                                    <span style={{ fontWeight: 700 }}>{layouts.find(l => l.id === selectedPlotId)?.name}</span>
                                </div>
                            )}
                        </div>
                    ) : (
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
                                        <p>Drop the original allotment map here</p>
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
                            <div className="label" style={{ marginTop: 8 }}>📌 Manual Reference Map</div>
                        </div>
                    )}

                    {/* Satellite Image (Always Visible) */}
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
                                    <p>Drop the latest satellite or drone image here</p>
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
                        disabled={!satImage || (uploadMode === 'manual' && !refImage) || (uploadMode === 'registry' && !selectedPlotId) || uploading}
                        onClick={handleSubmit}
                    >
                        {uploading ? '⏳ Analyzing...' : '🔍 Run Change Detection'}
                    </button>
                    {uploading && <p style={{ marginTop: 8, color: '#94a3b8', fontSize: 13 }}>Comparing {uploadMode === 'registry' ? 'Official Record' : 'Reference Map'} vs Satellite...</p>}
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

                        {/* ADVANCED INTELLIGENCE DASHBOARD (Phase 2) */}
                        {result.change_detection.financial_impact && (
                            <div className="glass-card" style={{ marginBottom: 20, padding: 16, background: 'rgba(30, 41, 59, 0.7)', border: '1px solid rgba(148, 163, 184, 0.2)' }}>
                                <h4 style={{ margin: '0 0 16px 0', color: '#60a5fa', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <span>🧠</span> Advanced Land Intelligence
                                </h4>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                                    {/* Industrial Health */}
                                    <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8 }}>
                                        <div style={{ fontSize: 12, color: '#94a3b8' }}>Industrial Health Index</div>
                                        <div style={{ fontSize: 24, fontWeight: 800, color: result.change_detection.industrial_health_index > 75 ? '#22c55e' : result.change_detection.industrial_health_index > 40 ? '#facc15' : '#ef4444' }}>
                                            {result.change_detection.industrial_health_index}/100
                                        </div>
                                    </div>
                                    {/* Classification */}
                                    <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8 }}>
                                        <div style={{ fontSize: 12, color: '#94a3b8' }}>Land Classification</div>
                                        <div style={{ fontSize: 16, fontWeight: 600, color: '#e2e8f0', marginTop: 6 }}>
                                            {result.change_detection.status.replace(/_/g, ' ').toUpperCase()}
                                        </div>
                                    </div>
                                    {/* Financial Loss */}
                                    <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8 }}>
                                        <div style={{ fontSize: 12, color: '#94a3b8' }}>Est. Revenue Leakage</div>
                                        <div style={{ fontSize: 18, fontWeight: 700, color: '#ef4444' }}>
                                            ₹{result.change_detection.financial_impact.estimated_revenue_leakage.toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div style={{ textAlign: 'center', marginBottom: 20 }}>
                            <a
                                href={getApiUrl(`/api/reports/${result.project_id}/pdf`)}
                                target="_blank"
                                className="btn-primary"
                                style={{ display: 'inline-flex', alignItems: 'center', gap: 8, textDecoration: 'none', padding: '10px 20px' }}
                            >
                                📄 Download Official Report
                            </a>
                        </div>

                        {/* PHASE 3: DECISION SUPPORT & GOVERNANCE */}
                        {result.audit_report && (
                            <div className="glass-card" style={{ marginBottom: 20, padding: 16 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                                    <h4 style={{ margin: 0, color: '#e2e8f0' }}>📋 Governance & Actions</h4>
                                    <button
                                        onClick={() => {
                                            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result.audit_report, null, 2));
                                            const downloadAnchorNode = document.createElement('a');
                                            downloadAnchorNode.setAttribute("href", dataStr);
                                            downloadAnchorNode.setAttribute("download", `audit_report_${result.project_id}.json`);
                                            document.body.appendChild(downloadAnchorNode);
                                            downloadAnchorNode.click();
                                            downloadAnchorNode.remove();
                                        }}
                                        className="upload-button"
                                        style={{ padding: '6px 12px', fontSize: 13, background: '#3b82f6' }}
                                    >
                                        Download Audit JSON
                                    </button>
                                </div>

                                <div style={{ background: 'rgba(15, 23, 42, 0.4)', borderRadius: 8, padding: 12 }}>
                                    <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                        Recommended Actions (Automated)
                                    </div>
                                    <ul style={{ margin: 0, paddingLeft: 20, color: '#cbd5e1' }}>
                                        {result.audit_report.compliance.recommended_actions.map((action, idx) => (
                                            <li key={idx} style={{ marginBottom: 4 }}>{action}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}

                        {/* Result Images */}
                        <div className="analysis-grid">
                            <div className="analysis-image-card">
                                <div className="card-header">🔥 Encroachment Heatmap</div>
                                <img src={getApiUrl(result.outputs.heatmap)} alt="Heatmap" />
                            </div>
                            <div className="analysis-image-card">
                                <div className="card-header">🎯 Approved Boundary (Green)</div>
                                <img src={getApiUrl(result.outputs.comparison)} alt="Comparison" />
                            </div>
                            <div className="analysis-image-card">
                                <div className="card-header">💀 Encroachment Mask (Binary)</div>
                                <img src={getApiUrl(result.outputs.mask)} alt="Mask" />
                            </div>
                            <div className="analysis-image-card">
                                <div className="card-header">↔️ Reference vs Satellite</div>
                                <img src={getApiUrl(result.outputs.comparison)} alt="Comparison" />
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
        </div >
    )
}

export default Upload

import { useState, useEffect } from 'react'
import { getApiUrl } from '../config'

function Analysis() {
    const [projects, setProjects] = useState([])
    const [selectedProject, setSelectedProject] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch(getApiUrl('/api/projects'))
            .then(res => res.json())
            .then(data => { setProjects(data); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    if (loading) return <div className="spinner"></div>

    return (
        <div>
            <div className="page-header">
                <h2>🔍 Analysis Results</h2>
                <p>View change detection results from uploaded image pairs</p>
            </div>

            <div style={{ marginTop: 24 }}>
                {projects.length === 0 ? (
                    <div className="glass-card">
                        <div className="empty-state">
                            <div className="empty-icon">🔬</div>
                            <h3>No Analysis Results Yet</h3>
                            <p style={{ marginTop: 8, color: '#94a3b8' }}>
                                Upload a reference map and satellite image to run change detection analysis.
                                Results will appear here.
                            </p>
                        </div>
                    </div>
                ) : (
                    <div>
                        {/* Project List */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 24 }}>
                            {projects.map(project => (
                                <div
                                    key={project.id}
                                    className={`glass-card ${selectedProject?.id === project.id ? '' : ''}`}
                                    style={{ cursor: 'pointer', padding: 16 }}
                                    onClick={() => setSelectedProject(project)}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <h4 style={{ fontSize: 15, marginBottom: 4 }}>{project.name}</h4>
                                            <p style={{ fontSize: 12, color: '#94a3b8' }}>
                                                Created: {new Date(project.created_at).toLocaleDateString('en-IN')} •
                                                Status: {project.status}
                                            </p>
                                        </div>
                                        {project.results && (
                                            <span className={`status-badge ${project.results.change_detection?.status || 'compliant'}`}>
                                                {(project.results.change_detection?.status || 'pending').replace(/_/g, ' ')}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Selected Project Results */}
                        {selectedProject?.results && (
                            <div className="animate-in">
                                <h3 style={{ marginBottom: 16 }}>Results: {selectedProject.name}</h3>

                                <div className="kpi-grid">
                                    <div className="kpi-card info">
                                        <div className="kpi-header"><span className="kpi-label">Change %</span></div>
                                        <div className="kpi-value">{selectedProject.results.change_detection.change_percentage}%</div>
                                    </div>
                                    <div className="kpi-card primary">
                                        <div className="kpi-header"><span className="kpi-label">Regions</span></div>
                                        <div className="kpi-value">{selectedProject.results.change_detection.num_change_regions}</div>
                                    </div>
                                    <div className="kpi-card success">
                                        <div className="kpi-header"><span className="kpi-label">Score</span></div>
                                        <div className="kpi-value">{selectedProject.results.compliance_score}</div>
                                    </div>
                                </div>

                                <div className="analysis-grid" style={{ marginTop: 16 }}>
                                    {Object.entries(selectedProject.results.outputs).map(([key, url]) => (
                                        <div key={key} className="analysis-image-card">
                                            <div className="card-header">{key.charAt(0).toUpperCase() + key.slice(1)}</div>
                                            <img src={url} alt={key} />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

export default Analysis

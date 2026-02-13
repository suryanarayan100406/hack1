import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, GeoJSON, Popup, useMap, ImageOverlay } from 'react-leaflet'

function FlyToArea({ center, zoom }) {
    const map = useMap()
    useEffect(() => {
        if (center) map.flyTo(center, zoom || 15, { duration: 1.5 })
    }, [center, zoom])
    return null
}

function MapView() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [selectedArea, setSelectedArea] = useState(null)
    const [mapCenter, setMapCenter] = useState([21.2750, 81.5650])
    const [mapZoom, setMapZoom] = useState(10)
    const [selectedPlot, setSelectedPlot] = useState(null)
    const [basemap, setBasemap] = useState('satellite')

    useEffect(() => {
        fetch('/api/demo-data')
            .then(res => res.json())
            .then(d => { setData(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    if (loading) return <div className="spinner"></div>
    if (!data) return <div className="empty-state"><h3>Could not load map data</h3></div>

    const { areas, geojson } = data

    const getColor = (status) => {
        switch (status) {
            case 'compliant': return '#10b981'
            case 'violation': return '#ef4444'
            case 'vacant': return '#8b5cf6'
            default: return '#6366f1'
        }
    }

    const onEachFeature = (feature, layer) => {
        layer.on('click', () => {
            setSelectedPlot(feature.properties)
        })
    }

    const geoJsonStyle = (feature) => ({
        color: getColor(feature.properties.status),
        weight: 2,
        opacity: 0.9,
        fillColor: getColor(feature.properties.status),
        fillOpacity: 0.25,
    })

    const filteredGeoJson = selectedArea
        ? { ...geojson, features: geojson.features.filter(f => f.properties.area_id === selectedArea) }
        : geojson

    const handleAreaClick = (area) => {
        setSelectedArea(area.id === selectedArea ? null : area.id)
        setMapCenter(area.center)
        setMapZoom(area.zoom)
        setSelectedPlot(null)
    }

    const tileUrls = {
        satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        street: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        terrain: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    }

    return (
        <div>
            <div className="page-header">
                <h2>🗺️ Interactive Map</h2>
                <p>Satellite-based view of all industrial areas with plot boundary overlays</p>
            </div>

            <div className="map-page" style={{ marginTop: 16 }}>
                <div className="map-main">
                    {/* Basemap Toggle */}
                    <div className="map-controls">
                        {Object.keys(tileUrls).map(key => (
                            <button
                                key={key}
                                className={`map-btn ${basemap === key ? 'active' : ''}`}
                                onClick={() => setBasemap(key)}
                            >
                                {key === 'satellite' ? '🛰️' : key === 'street' ? '🗺️' : '⛰️'} {key.charAt(0).toUpperCase() + key.slice(1)}
                            </button>
                        ))}
                    </div>

                    {/* Area Selector */}
                    <div className="area-selector">
                        <button
                            className={`area-chip ${!selectedArea ? 'active' : ''}`}
                            onClick={() => { setSelectedArea(null); setMapCenter([21.5, 81.7]); setMapZoom(8) }}
                        >
                            All Areas
                        </button>
                        {areas.map(area => (
                            <button
                                key={area.id}
                                className={`area-chip ${selectedArea === area.id ? 'active' : ''}`}
                                onClick={() => handleAreaClick(area)}
                            >
                                {area.name.replace(' Industrial Area', '')}
                            </button>
                        ))}
                    </div>

                    {/* Map */}
                    <div className="map-container" style={{ flex: 1 }}>
                        <MapContainer
                            center={mapCenter}
                            zoom={mapZoom}
                            scrollWheelZoom={true}
                            style={{ height: '100%', width: '100%' }}
                        >
                            <TileLayer
                                url={tileUrls[basemap]}
                                attribution='&copy; ESRI'
                                maxZoom={19}
                            />
                            <FlyToArea center={mapCenter} zoom={mapZoom} />
                            {filteredGeoJson && (
                                <>
                                    <GeoJSON
                                        key={selectedArea || 'all'}
                                        data={filteredGeoJson}
                                        style={geoJsonStyle}
                                        onEachFeature={onEachFeature}
                                    />
                                    {/* Render Image Overlays for Violations */}
                                    {filteredGeoJson.features.map(feature => {
                                        if (feature.properties.overlay_url && feature.properties.bounds) {
                                            return (
                                                <ImageOverlay
                                                    key={`overlay-${feature.properties.id}`}
                                                    url={feature.properties.overlay_url}
                                                    bounds={feature.properties.bounds}
                                                    opacity={0.8}
                                                    zIndex={1000}
                                                />
                                            )
                                        }
                                        return null
                                    })}
                                </>
                            )}
                        </MapContainer>
                    </div>
                </div>

                {/* Side Panel */}
                <div className="map-sidebar-panel">
                    {selectedPlot ? (
                        <div className="plot-info-panel animate-in">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                                <h4>{selectedPlot.name}</h4>
                                <span className={`status-badge ${selectedPlot.status}`}>{selectedPlot.status}</span>
                            </div>

                            {/* Analysis Image Preview */}
                            {selectedPlot.overlay_url && (
                                <div style={{ marginBottom: 12, borderRadius: 8, overflow: 'hidden', border: '1px solid #334155' }}>
                                    <div style={{ fontSize: 11, background: '#1e293b', padding: '4px 8px', color: '#94a3b8' }}>
                                        Analysis Heatmap
                                    </div>
                                    <img
                                        src={selectedPlot.overlay_url}
                                        alt="Analysis Overlay"
                                        style={{ width: '100%', display: 'block' }}
                                        onError={(e) => {
                                            e.target.style.display = 'none';
                                            console.error("Failed to load overlay image:", selectedPlot.overlay_url);
                                        }}
                                    />
                                </div>
                            )}

                            <div className="plot-detail-row">
                                <span className="plot-detail-label">Plot ID</span>
                                <span className="plot-detail-value">{selectedPlot.id}</span>
                            </div>
                            {selectedPlot.violation_type && (
                                <div className="plot-detail-row">
                                    <span className="plot-detail-label">Violation Type</span>
                                    <span className="plot-detail-value" style={{ color: '#ef4444' }}>
                                        {selectedPlot.violation_type.replace(/_/g, ' ')}
                                    </span>
                                </div>
                            )}
                            <div className="plot-detail-row">
                                <span className="plot-detail-label">Allotted Area</span>
                                <span className="plot-detail-value">{selectedPlot.allotted_area_sqm.toLocaleString()} sqm</span>
                            </div>
                            <div className="plot-detail-row">
                                <span className="plot-detail-label">Current Area</span>
                                <span className="plot-detail-value">{selectedPlot.current_area_sqm.toLocaleString()} sqm</span>
                            </div>
                            <div className="plot-detail-row">
                                <span className="plot-detail-label">Deviation</span>
                                <span className="plot-detail-value" style={{
                                    color: selectedPlot.deviation_pct > 10 ? '#ef4444' : selectedPlot.deviation_pct > 0 ? '#f59e0b' : '#10b981'
                                }}>
                                    {selectedPlot.deviation_pct}%
                                </span>
                            </div>
                            <div className="plot-detail-row">
                                <span className="plot-detail-label">Compliance Score</span>
                                <div className="score-gauge">
                                    <div className={`score-circle ${selectedPlot.compliance_score >= 70 ? 'score-high' : selectedPlot.compliance_score >= 40 ? 'score-mid' : 'score-low'}`}>
                                        {selectedPlot.compliance_score}
                                    </div>
                                </div>
                            </div>
                            <div className="plot-detail-row">
                                <span className="plot-detail-label">Lease Status</span>
                                <span className="plot-detail-value" style={{
                                    color: selectedPlot.lease_status === 'current' ? '#10b981' : '#ef4444'
                                }}>
                                    {selectedPlot.lease_status === 'current' ? '✅ Current' : '⚠️ Overdue'}
                                </span>
                            </div>
                            <div className="plot-detail-row">
                                <span className="plot-detail-label">Last Payment</span>
                                <span className="plot-detail-value">{selectedPlot.last_payment}</span>
                            </div>
                            <div className="plot-detail-row">
                                <span className="plot-detail-label">Last Checked</span>
                                <span className="plot-detail-value">{selectedPlot.last_checked}</span>
                            </div>
                            {selectedPlot.violation_type && (
                                <div className="plot-detail-row">
                                    <span className="plot-detail-label">Violation Type</span>
                                    <span className="plot-detail-value" style={{ color: '#ef4444' }}>
                                        {selectedPlot.violation_type.replace(/_/g, ' ')}
                                    </span>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="plot-info-panel">
                            <div className="empty-state" style={{ padding: '30px 10px' }}>
                                <div className="empty-icon">👆</div>
                                <h3>Select a Plot</h3>
                                <p style={{ fontSize: 13 }}>Click on any plot boundary on the map to view details</p>
                            </div>
                        </div>
                    )}

                    {/* Legend */}
                    <div className="plot-info-panel">
                        <h4 style={{ marginBottom: 12, fontSize: 14 }}>🎨 Map Legend</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            {[
                                { color: '#10b981', label: 'Compliant — Within approved boundaries' },
                                { color: '#ef4444', label: 'Violation — Encroachment / unauthorized' },
                                { color: '#8b5cf6', label: 'Vacant — Allotted but unused' },
                            ].map(item => (
                                <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12 }}>
                                    <div style={{ width: 16, height: 16, borderRadius: 4, background: item.color, flexShrink: 0 }}></div>
                                    <span style={{ color: '#94a3b8' }}>{item.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default MapView

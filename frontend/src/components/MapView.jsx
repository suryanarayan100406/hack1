import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { getApiUrl } from '../config'

// Fix Leaflet Default Icon
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

function MapView({ onSelectDistrict }) {
    const [geoJsonData, setGeoJsonData] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch(getApiUrl('/api/registry/geojson'))
            .then(res => res.json())
            .then(data => {
                setGeoJsonData(data)
                setLoading(false)
            })
            .catch(err => {
                console.error("Failed to load map data", err)
                setLoading(false)
            })
    }, [])

    const onEachFeature = (feature, layer) => {
        const name = feature.properties.dist_e || feature.id;

        layer.bindPopup(`
            <div style="text-align: center;">
                <strong>${name}</strong><br/>
                <button 
                    onclick="window.districtSelect('${feature.id}')"
                    style="margin-top: 5px; padding: 4px 8px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Analyze This Area
                </button>
            </div>
        `)

        layer.on({
            mouseover: (e) => {
                const layer = e.target;
                layer.setStyle({
                    weight: 3,
                    color: '#60a5fa',
                    dashArray: '',
                    fillOpacity: 0.6
                });
            },
            mouseout: (e) => {
                const layer = e.target;
                layer.setStyle({
                    weight: 1,
                    color: '#3388ff',
                    fillOpacity: 0.2
                });
            }
        });
    }

    // Expose select function globally for popup button
    useEffect(() => {
        window.districtSelect = (id) => {
            if (onSelectDistrict) onSelectDistrict(id)
        }
        return () => {
            delete window.districtSelect
        }
    }, [onSelectDistrict])

    if (loading) return <div className="spinner">Loading Map...</div>

    return (
        <div style={{ height: '500px', width: '100%', borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(148,163,184,0.2)' }}>
            <MapContainer
                center={[21.27, 81.60]}
                zoom={7}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {geoJsonData && (
                    <GeoJSON
                        data={geoJsonData}
                        style={{
                            color: '#3388ff',
                            weight: 1,
                            fillColor: '#3388ff',
                            fillOpacity: 0.2
                        }}
                        onEachFeature={onEachFeature}
                    />
                )}
            </MapContainer>
        </div>
    )
}

export default MapView

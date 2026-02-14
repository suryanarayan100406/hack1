import { useState } from 'react'

function Login({ onLogin }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault()
        if (username === 'admin' && password === 'admin') {
            onLogin()
        } else {
            setError('Invalid credentials')
        }
    }

    return (
        <div style={{
            height: '100vh',
            width: '100vw',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
            color: '#f8fafc'
        }}>
            <div className="glass-card" style={{
                width: 400,
                padding: 40,
                display: 'flex',
                flexDirection: 'column',
                gap: 20
            }}>
                <div style={{ textAlign: 'center', marginBottom: 10 }}>
                    <div style={{ fontSize: 48, marginBottom: 10 }}>🛡️</div>
                    <h2 style={{ fontSize: 24, fontWeight: 700 }}>Land Sentinel</h2>
                    <p style={{ color: '#94a3b8' }}>Secure Content Access</p>
                </div>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div>
                        <label className="form-label">Username</label>
                        <input
                            type="text"
                            className="form-input"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                            autoFocus
                        />
                    </div>
                    <div>
                        <label className="form-label">Password</label>
                        <input
                            type="password"
                            className="form-input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter password"
                        />
                    </div>

                    {error && <div style={{ color: '#ef4444', fontSize: 13, textAlign: 'center' }}>{error}</div>}

                    <button type="submit" className="btn-primary" style={{ marginTop: 10 }}>
                        Login
                    </button>

                    <div style={{ textAlign: 'center', marginTop: 10, fontSize: 12, color: '#64748b' }}>
                        CSIDC Internal System • Authorized Use Only
                    </div>
                </form>
            </div>
        </div>
    )
}

export default Login

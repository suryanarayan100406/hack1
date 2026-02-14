// API Base URL Configuration

// For local development with Vite proxy, use relative path.
// For production (Netlify), this must be changed to the Ngrok/Live Backend URL.
// Example: "https://your-ngrok-url.ngrok-free.app"

const IS_PROD = import.meta.env.PROD;

// Priority: 1. Environment Variable (Netlify/Vercel) -> 2. Hardcoded Fallback -> 3. Proxy (Local)
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (IS_PROD
    ? "https://your-render-backend.onrender.com" // Update this if Env Var is not set
    : "");

export const getApiUrl = (endpoint) => {
    // Determine if endpoint starts with /
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${API_BASE_URL}${path}`;
}

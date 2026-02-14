// API Base URL Configuration

// For local development with Vite proxy, use relative path.
// For production (Netlify), this must be changed to the Ngrok/Live Backend URL.
// Example: "https://your-ngrok-url.ngrok-free.app"

const IS_PROD = import.meta.env.PROD;

export const API_BASE_URL = IS_PROD
    ? "REPLACE_WITH_YOUR_NGROK_URL" // User must update this before deploy
    : ""; // Empty string means use relative path (proxy)

export const getApiUrl = (endpoint) => {
    // Determine if endpoint starts with /
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${API_BASE_URL}${path}`;
}

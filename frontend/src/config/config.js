const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  tokenKey: 'access_token',
  refreshTokenKey: 'refresh_token',
  userKey: 'user_data',
};

export default config;

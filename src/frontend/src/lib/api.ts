const getApiBaseUrl = (): string => {
  // In production (when window is defined and not localhost), use the hosted backend
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return 'https://backend-stock-market-positions-aler.vercel.app';
    }
  }
  
  // For development or server-side rendering, use localhost
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();

export const apiEndpoints = {
  stocks: `${API_BASE_URL}/api/stocks`,
  stockDetails: (ticker: string) => `${API_BASE_URL}/api/stocks/${ticker}`,
}; 
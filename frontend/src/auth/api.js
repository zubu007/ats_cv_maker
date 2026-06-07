const inferredApiBaseUrl = `${window.location.protocol}//${window.location.hostname}:8000`;

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || inferredApiBaseUrl;

export async function apiRequest(path, options = {}) {
  const { method = 'GET', body, headers = {} } = options;

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      credentials: 'include',
      headers: {
        ...(body ? { 'Content-Type': 'application/json' } : {}),
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    throw new Error(`Could not reach backend at ${API_BASE_URL}. Check that the API server is running.`);
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message = payload.detail || payload.message || 'Request failed';
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    return null;
  }

  return response.json();
}

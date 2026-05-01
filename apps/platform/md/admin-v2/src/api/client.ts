import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach Authorization header
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sillymd_admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: normalize flat responses from backend to {success, data}
apiClient.interceptors.response.use(
  (response) => {
    // Backend modules often return flat objects like {id, title, content} without
    // the {success, data} wrapper.  Normalize them, but skip auth responses.
    const body = response.data;
    if (body && typeof body === 'object' && !('success' in body) && !('access_token' in body)) {
      response.data = { success: true, data: body };
    }
    return response;
  },
  (error) => {
    if (error.response) {
      const { status } = error.response;

      if (status === 401) {
        localStorage.removeItem('sillymd_admin_token');
        localStorage.removeItem('sillymd_admin_user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

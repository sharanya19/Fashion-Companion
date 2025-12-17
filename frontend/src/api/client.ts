import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000',  // Use IP instead of localhost for Windows compatibility
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const analyzePhoto = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/profile/analyze-photo', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};

export default api;

import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
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

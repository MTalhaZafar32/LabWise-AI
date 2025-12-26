/**
 * API Service for LabWise AI
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'multipart/form-data',
    },
});

export const api = {
    /**
     * Check API health status
     */
    async checkHealth() {
        const response = await apiClient.get('/health');
        return response.data;
    },

    /**
     * Analyze lab report
     * @param {File} file - Lab report file (PDF or image)
     */
    async analyzeReport(file, onProgress) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await apiClient.post('/analyze', formData, {
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                );
                if (onProgress) {
                    onProgress(percentCompleted);
                }
            },
        });

        return response.data;
    },
};

export default api;

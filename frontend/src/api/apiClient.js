import axios from 'axios';

const apiHost = import.meta.env.VITE_API_HOST;


export const apiClient = axios.create({
    baseURL: `http://${apiHost}`,
    headers: {
        'Content-Type': 'application/json',
    },
});
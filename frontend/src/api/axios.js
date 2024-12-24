// src/api/axios.js
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1/', // Updated to match your backend API URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;

import axios from 'axios';

// base url for all api requests 
const API_URL = 'http://localhost:8000/api';

//creating an api instance with out configuration
const api = axios.create({
  baseURL: API_URL,
});

export default api;
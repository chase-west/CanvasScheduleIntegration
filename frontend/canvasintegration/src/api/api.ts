import axios, { AxiosInstance } from 'axios';

const baseURL = 'https://localhost:5000'; // Update with your Flask backend URL

// Create an Axios instance with a base URL
const api: AxiosInstance = axios.create({
  baseURL,
});

// Function to fetch Microsoft token
export const fetchMicrosoftToken = async (code: string) => {
  const response = await api.get(`/callback/microsoft?code=${code}`);
  return response.data;
};

// Function to fetch Google token
export const fetchGoogleToken = async (code: string) => {
  const response = await api.get(`/callback/google?code=${code}`);
  return response.data;
};

// Function to login to Canvas
export const loginToCanvas = async (credentials: { email: string; password: string }) => {
  try {
    const response = await api.post('/api/login/canvas', credentials);
    return response.data; // Ensure response.data is defined before accessing it
  } catch (error : any) {
    // Handle specific errors if necessary
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      throw error.response.data;
    } else if (error.request) {
      // The request was made but no response was received
      throw 'No response received from server.';
    } else {
      // Something happened in setting up the request that triggered an Error
      throw 'Error setting up the request.';
    }
  }
};

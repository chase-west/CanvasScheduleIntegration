import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000',
});

export const fetchMicrosoftToken = async (code: string) => {
  const response = await api.get(`/callback/microsoft?code=${code}`);
  return response.data;
};

export const fetchGoogleToken = async (code: string) => {
  const response = await api.get(`/callback/google?code=${code}`);
  return response.data;
};

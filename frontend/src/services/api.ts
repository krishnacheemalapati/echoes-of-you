import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Adjust the base URL as needed
  headers: {
    'Content-Type': 'application/json',
  },
});

// Example API call to get data
export const getData = async () => {
  try {
    const response = await api.get('/data'); // Adjust the endpoint as needed
    return response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
};

// Example API call to create data
export const createData = async (data: any) => {
  try {
    const response = await api.post('/data', data); // Adjust the endpoint as needed
    return response.data;
  } catch (error) {
    console.error('Error creating data:', error);
    throw error;
  }
};

// Add more API functions as needed

export default {
  getData,
  createData,
};
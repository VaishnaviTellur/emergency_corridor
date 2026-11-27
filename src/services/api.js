import axios from 'axios'

const API = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000,
})

export const getBackendStatus = async () => {
  const response = await API.get('/api/status')
  return response.data
}

export default API
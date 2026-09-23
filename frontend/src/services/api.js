import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const projectService = {
  createProject: async (name, sourcePath) => {
    const response = await api.post('/projects', { name, source_path: sourcePath });
    return response.data.data;
  },
  
  getProjects: async () => {
    const response = await api.get('/projects');
    return response.data.data;
  },
  
  getProjectStatus: async (projectId) => {
    const response = await api.get(`/projects/${projectId}/status`);
    return response.data.data;
  },
};

export default api;

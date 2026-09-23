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
  
  uploadProject: async (name, files) => {
    const formData = new FormData();
    formData.append('name', name);
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });
    
    const response = await api.post('/projects/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
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

export const photoService = {
  getStats: async (projectId) => {
    const response = await api.get(`/photos/project/${projectId}/stats`);
    return response.data.data;
  },
  
  getPhotos: async (projectId, params = {}) => {
    const response = await api.get(`/photos`, { 
      params: { project_id: projectId, ...params } 
    });
    return response.data;
  },
  
  getPhotoDetail: async (photoId) => {
    const response = await api.get(`/photos/${photoId}`);
    return response.data.data;
  },
  
  updateCategory: async (photoId, category) => {
    const response = await api.patch(`/photos/${photoId}/category`, { category });
    return response.data.data;
  }
};

export const duplicateService = {
  getGroups: async (projectId) => {
    const response = await api.get(`/duplicates/project/${projectId}`);
    return response.data.data;
  }
};

export const exportService = {
  startExport: async (projectId, destinationPath, categories) => {
    const response = await api.post('/export', {
      project_id: projectId,
      destination_path: destinationPath,
      categories: categories
    });
    return response.data.data;
  },
  
  getExportStatus: async (taskId) => {
    const response = await api.get(`/export/${taskId}`);
    return response.data.data;
  }
};

export default api;

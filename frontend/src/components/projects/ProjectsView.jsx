import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FolderOpen, 
  Trash, 
  WarningCircle,
  FolderDashed,
  ArrowRight
} from '@phosphor-icons/react';
import { projectService } from '../../services/api';
import './ProjectsView.css';

const ProjectsView = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeProjectId, setActiveProjectId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
    const stored = localStorage.getItem('activeProjectId');
    if (stored) {
      setActiveProjectId(parseInt(stored));
    }
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await projectService.getProjects();
      setProjects(data);
      if (data && data.length > 0) {
        if (!localStorage.getItem('activeProjectId')) {
          localStorage.setItem('activeProjectId', data[0].id);
          setActiveProjectId(data[0].id);
        }
      }
      setError(null);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
      setError('Could not load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, projectId) => {
    e.stopPropagation(); // Prevent opening the project
    
    if (window.confirm('Are you sure you want to delete this project? This will remove all associated data.')) {
      try {
        await projectService.deleteProject(projectId);
        // Remove from UI
        setProjects(projects.filter(p => p.id !== projectId));
      } catch (err) {
        console.error('Failed to delete project:', err);
        alert('Failed to delete project.');
      }
    }
  };

  const handleOpenProject = (projectId) => {
    localStorage.setItem('activeProjectId', projectId);
    setActiveProjectId(projectId);
    navigate(`/dashboard?projectId=${projectId}`);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="view-container projects-loading">
        <div className="projects-spinner"></div>
        <p>Loading projects...</p>
      </div>
    );
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <div className="view-title">
          <FolderOpen size={24} weight="fill" className="text-primary" />
          <h2>My Projects</h2>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <WarningCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {projects.length === 0 && !error ? (
        <div className="empty-state">
          <FolderDashed size={64} weight="light" />
          <h3>No Projects Found</h3>
          <p>You haven't created any projects yet.</p>
          <button className="btn btn-primary" onClick={() => navigate('/import')}>
            Create New Project
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div 
              key={project.id} 
              className="project-card"
              onClick={() => handleOpenProject(project.id)}
            >
              <div className="project-card-header">
                <h3>{project.name}</h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {activeProjectId === project.id && (
                    <span className="status-badge" style={{ backgroundColor: 'var(--interactive-primary)', color: 'white' }}>
                      Active
                    </span>
                  )}
                  <span className={`status-badge status-${project.status}`}>
                    {project.status}
                  </span>
                </div>
              </div>
              
              <div className="project-card-body">
                <div className="project-stat">
                  <span className="stat-label">Source</span>
                  <span className="stat-value truncate" title={project.source_path}>
                    {project.source_path}
                  </span>
                </div>
                <div className="project-stat">
                  <span className="stat-label">Total Files</span>
                  <span className="stat-value">{project.total_files}</span>
                </div>
                <div className="project-stat">
                  <span className="stat-label">Created</span>
                  <span className="stat-value">{formatDate(project.created_at)}</span>
                </div>
              </div>
              
              <div className="project-card-footer">
                <button 
                  className="btn btn-danger" 
                  onClick={(e) => handleDelete(e, project.id)}
                  title="Delete Project"
                >
                  <Trash size={18} /> Delete
                </button>
                <button 
                  className="btn btn-primary" 
                  onClick={() => handleOpenProject(project.id)}
                  title="Open Project"
                >
                  Open <ArrowRight size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectsView;

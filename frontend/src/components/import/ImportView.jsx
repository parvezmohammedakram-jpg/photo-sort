import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderOpen, WarningCircle } from '@phosphor-icons/react';
import { projectService } from '../../services/api';
import './ImportView.css';

const ImportView = () => {
  const navigate = useNavigate();
  const [folderPath, setFolderPath] = useState('');
  const [projectName, setProjectName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleImport = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!folderPath || !projectName) {
      setError('Please provide both a project name and a folder path.');
      return;
    }

    setIsLoading(true);
    try {
      const project = await projectService.createProject(projectName, folderPath);
      // Navigate to processing view with the new project ID
      navigate(`/processing?projectId=${project.id}`);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to create project and discover files. Please check the path and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="import-view">
      <div className="import-header">
        <h2>Import Photos</h2>
        <p>Start a new analysis session by pointing PhotoSort to a local folder.</p>
      </div>

      <div className="card import-card">
        <form onSubmit={handleImport}>
          <div className="input-group">
            <label className="input-label" htmlFor="projectName">Project Name</label>
            <input
              id="projectName"
              className="input"
              type="text"
              placeholder="e.g., Summer Wedding 2024"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="folderPath">Source Folder Path</label>
            <div className="path-input-wrapper">
              <FolderOpen className="path-icon" size={20} />
              <input
                id="folderPath"
                className="input path-input"
                type="text"
                placeholder="C:\Users\Name\Pictures\Event"
                value={folderPath}
                onChange={(e) => setFolderPath(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <p className="input-hint">
              Paste the absolute path to the directory containing your photos. 
              Subdirectories will be scanned automatically.
            </p>
          </div>

          {error && (
            <div className="error-message">
              <WarningCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          <div className="import-actions">
            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={isLoading || !folderPath || !projectName}
            >
              {isLoading ? 'Scanning Folder...' : 'Start Processing'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ImportView;

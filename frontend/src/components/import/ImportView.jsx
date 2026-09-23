import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderOpen, WarningCircle, UploadSimple, FileImage } from '@phosphor-icons/react';
import { projectService } from '../../services/api';
import './ImportView.css';

const ImportView = () => {
  const navigate = useNavigate();
  const [importMode, setImportMode] = useState('local'); // 'local' or 'upload'
  const [folderPath, setFolderPath] = useState('');
  const [projectName, setProjectName] = useState('');
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles(e.target.files);
    } else {
      setSelectedFiles(null);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleImport = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!projectName) {
      setError('Please provide a project name.');
      return;
    }

    if (importMode === 'local' && !folderPath) {
      setError('Please provide a folder path.');
      return;
    }

    if (importMode === 'upload' && (!selectedFiles || selectedFiles.length === 0)) {
      setError('Please select at least one photo to upload.');
      return;
    }

    setIsLoading(true);
    try {
      let project;
      if (importMode === 'local') {
        project = await projectService.createProject(projectName, folderPath);
      } else {
        project = await projectService.uploadProject(projectName, selectedFiles);
      }
      
      // Navigate to processing view with the new project ID
      navigate(`/processing?projectId=${project.id}`);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to create project. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="import-view">
      <div className="import-header">
        <h2>Import Photos</h2>
        <p>Start a new analysis session by pointing to a folder or uploading files.</p>
      </div>

      <div className="import-tabs">
        <button 
          type="button"
          className={`tab-btn ${importMode === 'local' ? 'active' : ''}`}
          onClick={() => setImportMode('local')}
        >
          <FolderOpen size={20} />
          Local Folder
        </button>
        <button 
          type="button"
          className={`tab-btn ${importMode === 'upload' ? 'active' : ''}`}
          onClick={() => setImportMode('upload')}
        >
          <UploadSimple size={20} />
          Upload Device Files
        </button>
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

          {importMode === 'local' ? (
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
          ) : (
            <div className="input-group">
              <label className="input-label">Select Photos to Upload</label>
              <input
                type="file"
                multiple
                accept="image/*"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileChange}
                disabled={isLoading}
              />
              <div 
                className={`upload-dropzone ${selectedFiles ? 'has-files' : ''}`} 
                onClick={!isLoading ? triggerFileInput : undefined}
              >
                <FileImage size={48} className="upload-icon" />
                {selectedFiles ? (
                  <p className="upload-text">{selectedFiles.length} file(s) selected</p>
                ) : (
                  <p className="upload-text">Click to browse photos from your device</p>
                )}
              </div>
              <p className="input-hint warning-hint">
                Uploading will copy files to the server. Large collections may take time to upload.
              </p>
            </div>
          )}

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
              disabled={
                isLoading || 
                !projectName || 
                (importMode === 'local' && !folderPath) ||
                (importMode === 'upload' && !selectedFiles)
              }
            >
              {isLoading ? (importMode === 'upload' ? 'Uploading & Scanning...' : 'Scanning Folder...') : 'Start Processing'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ImportView;

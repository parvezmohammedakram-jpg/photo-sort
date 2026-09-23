import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Export, 
  CheckCircle, 
  WarningCircle, 
  FolderOpen,
  Spinner,
  MagnifyingGlass,
  XCircle
} from '@phosphor-icons/react';
import { projectService, photoService, exportService } from '../../services/api';
import './ExportView.css';

const ExportView = () => {
  const navigate = useNavigate();
  const [projectId, setProjectId] = useState(null);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Export form state
  const [destPath, setDestPath] = useState('');
  const [categories, setCategories] = useState({
    good: true,
    review: false,
    poor: false
  });
  
  // Export progress state
  const [taskId, setTaskId] = useState(null);
  const [exportStatus, setExportStatus] = useState(null);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState(null);

  // Init project
  useEffect(() => {
    const initProject = async () => {
      try {
        const projects = await projectService.getProjects();
        if (projects && projects.length > 0) {
          const currentProjId = projects[0].id;
          setProjectId(currentProjId);
          
          const projectStats = await photoService.getStats(currentProjId);
          setStats(projectStats);
          
          // Suggest a default export path
          const sourcePath = projects[0].source_path;
          const defaultDest = sourcePath.endsWith('/') || sourcePath.endsWith('\\')
            ? `${sourcePath}PhotoSort_Export`
            : `${sourcePath}_PhotoSort_Export`;
          setDestPath(defaultDest);
        } else {
          navigate('/import');
        }
      } catch (error) {
        console.error('Error fetching project stats:', error);
        setError('Failed to load project data.');
      } finally {
        setIsLoading(false);
      }
    };
    initProject();
  }, [navigate]);

  // Poll export status
  useEffect(() => {
    if (!taskId) return;
    
    let interval;
    
    const checkStatus = async () => {
      try {
        const data = await exportService.getExportStatus(taskId);
        setExportStatus(data);
        
        if (data.status === 'completed' || data.status === 'failed') {
          setIsExporting(false);
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    };
    
    interval = setInterval(checkStatus, 1000);
    return () => clearInterval(interval);
  }, [taskId]);

  const handleCategoryToggle = (category) => {
    if (isExporting || (exportStatus && exportStatus.status === 'completed')) return;
    
    setCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const calculateSelectedCount = () => {
    if (!stats) return 0;
    let count = 0;
    if (categories.good) count += stats.categories.good;
    if (categories.review) count += stats.categories.review;
    if (categories.poor) count += stats.categories.poor;
    return count;
  };

  const handleExport = async (e) => {
    e.preventDefault();
    if (!destPath.trim()) return;
    
    const selectedCategories = Object.entries(categories)
      .filter(([_, isSelected]) => isSelected)
      .map(([cat]) => cat);
      
    if (selectedCategories.length === 0) {
      setError("Please select at least one category to export.");
      return;
    }
    
    setError(null);
    setIsExporting(true);
    setExportStatus(null);
    
    try {
      const data = await exportService.startExport(projectId, destPath, selectedCategories);
      setTaskId(data.task_id);
    } catch (err) {
      console.error(err);
      setError("Failed to start export process.");
      setIsExporting(false);
    }
  };

  const renderExportProgress = () => {
    if (!exportStatus) return null;
    
    const isDone = exportStatus.status === 'completed';
    const isFailed = exportStatus.status === 'failed';
    const progressPercent = exportStatus.total_files > 0 
      ? ((exportStatus.copied_files + exportStatus.failed_files) / exportStatus.total_files) * 100 
      : 100;
      
    return (
      <div className="card export-progress-card">
        <div className="export-progress-header">
          {isDone ? (
            <CheckCircle size={32} className="success-icon" />
          ) : isFailed ? (
            <WarningCircle size={32} className="error-icon" />
          ) : (
            <Spinner size={32} className="spinner" />
          )}
          <h3>
            {isDone ? 'Export Complete' : 
             isFailed ? 'Export Failed' : 
             'Exporting Photos...'}
          </h3>
        </div>
        
        <div className="progress-bar-container">
          <div 
            className={`progress-bar-fill ${isDone ? 'completed' : isFailed ? 'failed' : ''}`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        
        <div className="export-stats">
          <span>{exportStatus.copied_files} copied successfully</span>
          <span>{exportStatus.total_files} total files</span>
        </div>
        
        {exportStatus.failed_files > 0 && (
          <div className="export-error">
            <WarningCircle size={16} />
            <span>{exportStatus.failed_files} files failed to copy.</span>
          </div>
        )}
        
        {exportStatus.error_message && (
          <div className="export-error">
            {exportStatus.error_message}
          </div>
        )}
        
        {isDone && (
          <div className="export-actions">
            <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
              Return to Dashboard
            </button>
            <button className="btn btn-primary" onClick={() => {
              setTaskId(null);
              setExportStatus(null);
            }}>
              Export More
            </button>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return <div className="export-loading">Loading export options...</div>;
  }

  return (
    <div className="export-view">
      <div className="export-header">
        <h2>Export Photos</h2>
        <p className="subtitle">
          Safely copy categorized photos to a new folder. Original files are never modified or deleted.
        </p>
      </div>
      
      {error && (
        <div className="error-message">
          <WarningCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {taskId ? (
        renderExportProgress()
      ) : (
        <form className="card export-form" onSubmit={handleExport}>
          <div className="form-group">
            <label>Destination Folder Path</label>
            <div className="input-with-icon">
              <FolderOpen size={20} className="input-icon" />
              <input
                type="text"
                className="input"
                value={destPath}
                onChange={(e) => setDestPath(e.target.value)}
                placeholder="e.g. C:\Exports\Wedding_Selects"
                required
              />
            </div>
            <p className="help-text">A new folder will be created if it doesn't exist.</p>
          </div>
          
          <div className="form-group">
            <label>Select Categories to Export</label>
            <div className="category-selection">
              <div 
                className={`category-toggle ${categories.good ? 'active category-good' : ''}`}
                onClick={() => handleCategoryToggle('good')}
              >
                <div className="toggle-header">
                  <CheckCircle size={24} />
                  <span>Good</span>
                </div>
                <div className="toggle-count">{stats?.categories.good || 0} photos</div>
              </div>
              
              <div 
                className={`category-toggle ${categories.review ? 'active category-review' : ''}`}
                onClick={() => handleCategoryToggle('review')}
              >
                <div className="toggle-header">
                  <MagnifyingGlass size={24} />
                  <span>Review</span>
                </div>
                <div className="toggle-count">{stats?.categories.review || 0} photos</div>
              </div>
              
              <div 
                className={`category-toggle ${categories.poor ? 'active category-poor' : ''}`}
                onClick={() => handleCategoryToggle('poor')}
              >
                <div className="toggle-header">
                  <XCircle size={24} />
                  <span>Poor</span>
                </div>
                <div className="toggle-count">{stats?.categories.poor || 0} photos</div>
              </div>
            </div>
          </div>
          
          <div className="export-summary">
            <div className="summary-text">
              Selected <strong>{calculateSelectedCount()}</strong> photos for export.
            </div>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={calculateSelectedCount() === 0 || !destPath.trim()}
            >
              <Export size={20} />
              Start Export
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default ExportView;

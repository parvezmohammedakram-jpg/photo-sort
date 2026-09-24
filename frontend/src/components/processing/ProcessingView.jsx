import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Spinner, CheckCircle, WarningCircle } from '@phosphor-icons/react';
import { projectService } from '../../services/api';
import './ProcessingView.css';

const ProcessingView = () => {
  const navigate = useNavigate();
  const [projectIdStr] = useSearchParams();
  const [projectId, setProjectId] = useState(projectIdStr.get('projectId'));
  
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Auto-fetch latest project if accessed from sidebar without a projectId
  useEffect(() => {
    const initProject = async () => {
      if (!projectId) {
        try {
          const projects = await projectService.getProjects();
          if (projects && projects.length > 0) {
            const storedId = localStorage.getItem('activeProjectId');
            if (storedId && projects.find(p => p.id === parseInt(storedId))) {
              setProjectId(parseInt(storedId));
            } else {
              setProjectId(projects[0].id);
            }
          } else {
            navigate('/import');
          }
        } catch (error) {
          console.error('Error fetching projects:', error);
          setError('Failed to find an active project.');
        }
      }
    };
    initProject();
  }, [projectId, navigate]);

  useEffect(() => {
    if (!projectId) return;
    let isActive = true;
    let interval;

    const checkStatus = async () => {
      try {
        if (!isActive) return;
        const data = await projectService.getProjectStatus(projectId);
        setStatus(data);
        
        if (data.project_status === 'completed' || data.project_status === 'failed') {
          if (interval) clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
        if (isActive) setError('Failed to fetch processing status. The backend might be down.');
      }
    };

    // Initial check
    checkStatus();

    // Poll every 2 seconds
    interval = setInterval(checkStatus, 2000);

    return () => {
      isActive = false;
      if (interval) clearInterval(interval);
    };
  }, [projectId]);

  useEffect(() => {
    if (!status?.created_at) return;
    
    const calculateElapsed = () => {
      // Ensure UTC parsing by appending Z if it's missing (FastAPI often omits it)
      const startStr = status.created_at.endsWith('Z') ? status.created_at : `${status.created_at}Z`;
      const start = new Date(startStr).getTime();
      
      let end = Date.now();
      if (status.completed_at) {
        const endStr = status.completed_at.endsWith('Z') ? status.completed_at : `${status.completed_at}Z`;
        end = new Date(endStr).getTime();
      }
      
      setElapsedTime(Math.max(0, Math.floor((end - start) / 1000)));
    };
    
    calculateElapsed();
    
    if (status.project_status !== 'completed' && status.project_status !== 'failed') {
      const timer = setInterval(calculateElapsed, 1000);
      return () => clearInterval(timer);
    }
  }, [status]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (error) {
    return (
      <div className="processing-view error-state">
        <WarningCircle size={48} className="error-icon" />
        <h2>Processing Error</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={() => navigate('/import')}>
          Return to Import
        </button>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="processing-view loading-state">
        <Spinner size={48} className="spinner" />
        <h2>Connecting to Engine...</h2>
      </div>
    );
  }

  const isCompleted = status.project_status === 'completed';
  const progressPercent = status.progress_percent || 0;

  return (
    <div className="processing-view">
      <div className="processing-header">
        {isCompleted ? (
          <CheckCircle size={48} className="success-icon" />
        ) : (
          <Spinner size={48} className="spinner" />
        )}
        <h2>{isCompleted ? 'Analysis Complete' : 'Analyzing Photographs'}</h2>
        <p>
          {isCompleted 
            ? 'Redirecting to results...' 
            : 'Applying blur detection, exposure analysis, and facial recognition.'}
        </p>
      </div>

      <div className="card progress-card">
        <div className="progress-stats">
          <div className="stat">
            <span className="stat-value">{status.processed}</span>
            <span className="stat-label">Processed</span>
          </div>
          <div className="stat divider">/</div>
          <div className="stat">
            <span className="stat-value">{status.total}</span>
            <span className="stat-label">Total Images</span>
          </div>
        </div>

        <div className="progress-bar-container">
          <div 
            className={`progress-bar-fill ${isCompleted ? 'completed' : ''}`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        
        <div className="progress-footer">
          <div className="progress-footer-left">
            <span>{progressPercent.toFixed(1)}% Complete</span>
            <span className="elapsed-time" style={{ marginLeft: '1rem', color: 'var(--text-muted)' }}>
              Time: {formatTime(elapsedTime)}
            </span>
          </div>
          {status.failed > 0 && (
            <span className="error-text">{status.failed} failed</span>
          )}
        </div>
      </div>
      
      {isCompleted && (
        <div className="processing-actions" style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center' }}>
          <button 
            className="btn btn-primary" 
            onClick={() => navigate(`/results?projectId=${projectId}`)}
            style={{ fontSize: '1.1rem', padding: '0.75rem 2rem' }}
          >
            View Results
          </button>
        </div>
      )}
    </div>
  );
};

export default ProcessingView;

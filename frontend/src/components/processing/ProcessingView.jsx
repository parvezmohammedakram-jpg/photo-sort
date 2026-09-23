import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Spinner, CheckCircle, WarningCircle } from '@phosphor-icons/react';
import { projectService } from '../../services/api';
import './ProcessingView.css';

const ProcessingView = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get('projectId');
  
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!projectId) {
      navigate('/import');
      return;
    }

    const checkStatus = async () => {
      try {
        const data = await projectService.getProjectStatus(projectId);
        setStatus(data);
        
        if (data.project_status === 'completed') {
          // Add a small delay for UX before redirecting
          setTimeout(() => {
            navigate(`/results?projectId=${projectId}`);
          }, 1500);
        }
      } catch (err) {
        console.error(err);
        setError('Failed to fetch processing status. The backend might be down.');
      }
    };

    // Initial check
    checkStatus();

    // Poll every 2 seconds if not completed/failed
    const interval = setInterval(() => {
      if (!status || (status.project_status !== 'completed' && status.project_status !== 'failed')) {
        checkStatus();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [projectId, navigate, status?.project_status]);

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
          <span>{progressPercent.toFixed(1)}% Complete</span>
          {status.failed > 0 && (
            <span className="error-text">{status.failed} failed</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProcessingView;

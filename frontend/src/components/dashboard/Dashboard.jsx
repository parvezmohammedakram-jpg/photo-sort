import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Images, 
  CheckCircle, 
  WarningCircle, 
  MagnifyingGlass,
  XCircle,
  Copy,
  Star
} from '@phosphor-icons/react';
import { projectService, photoService } from '../../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const projects = await projectService.getProjects();
        if (projects && projects.length > 0) {
          const latestProject = projects[0];
          setProject(latestProject);
          
          if (latestProject.status === 'completed') {
            const projectStats = await photoService.getStats(latestProject.id);
            setStats(projectStats);
          } else {
            // Still processing or pending
            navigate(`/processing?projectId=${latestProject.id}`);
          }
        }
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [navigate]);

  if (isLoading) {
    return <div className="dashboard-loading">Loading...</div>;
  }

  if (!project) {
    return (
      <div className="dashboard-empty">
        <Images size={64} className="empty-icon" />
        <h2>No Projects Found</h2>
        <p>Start by importing a folder of photographs to analyze.</p>
        <button 
          className="btn btn-primary" 
          onClick={() => navigate('/import')}
          style={{ marginTop: '24px' }}
        >
          Import Photos
        </button>
      </div>
    );
  }

  if (!stats) return null;

  const total = stats.total_photos;
  const { good, review, poor } = stats.categories;
  
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h2 className="project-title">{project.name}</h2>
          <p className="project-path">{project.source_path}</p>
        </div>
        <button className="btn btn-secondary" onClick={() => navigate('/import')}>
          New Project
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card total-card">
          <div className="stat-card-icon"><Images size={24} /></div>
          <div className="stat-card-value">{total}</div>
          <div className="stat-card-label">Total Photos</div>
        </div>
        
        <div className="stat-card score-card">
          <div className="stat-card-icon"><Star size={24} /></div>
          <div className="stat-card-value">{stats.average_quality_score}</div>
          <div className="stat-card-label">Avg Quality Score</div>
        </div>
      </div>

      <h3 className="section-title">Categorization</h3>
      <div className="category-grid">
        <div className="category-card good-card" onClick={() => navigate('/results?category=good')}>
          <div className="category-header">
            <CheckCircle size={24} />
            <span>Good</span>
          </div>
          <div className="category-value">{good}</div>
          <div className="category-bar">
            <div className="category-bar-fill" style={{ width: `${(good/total)*100}%` }}></div>
          </div>
        </div>

        <div className="category-card review-card" onClick={() => navigate('/results?category=review')}>
          <div className="category-header">
            <MagnifyingGlass size={24} />
            <span>Review</span>
          </div>
          <div className="category-value">{review}</div>
          <div className="category-bar">
            <div className="category-bar-fill" style={{ width: `${(review/total)*100}%` }}></div>
          </div>
        </div>

        <div className="category-card poor-card" onClick={() => navigate('/results?category=poor')}>
          <div className="category-header">
            <XCircle size={24} />
            <span>Poor</span>
          </div>
          <div className="category-value">{poor}</div>
          <div className="category-bar">
            <div className="category-bar-fill" style={{ width: `${(poor/total)*100}%` }}></div>
          </div>
        </div>
      </div>

      <div className="issues-section">
        <div className="issues-header">
          <h3 className="section-title">Detected Issues</h3>
        </div>
        
        <div className="issues-grid">
          <div className="issue-card" onClick={() => navigate('/results')}>
            <span className="issue-count">{stats.issues.blur}</span>
            <span className="issue-label">Blurry or Out of Focus</span>
          </div>
          
          <div className="issue-card" onClick={() => navigate('/results')}>
            <span className="issue-count">{stats.issues.exposure}</span>
            <span className="issue-label">Exposure Issues</span>
          </div>
          
          <div className="issue-card" onClick={() => navigate('/results')}>
            <span className="issue-count">{stats.issues.eyes_closed}</span>
            <span className="issue-label">Closed Eyes Detected</span>
          </div>
          
          <div className="issue-card duplicate-card" onClick={() => navigate('/duplicates')}>
            <div className="duplicate-icon"><Copy size={24} /></div>
            <div className="duplicate-info">
              <span className="issue-count">{stats.duplicate_photos}</span>
              <span className="issue-label">Photos in {stats.duplicate_groups} duplicate groups</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

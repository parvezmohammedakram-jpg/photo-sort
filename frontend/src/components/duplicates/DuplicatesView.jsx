import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Copy, WarningCircle } from '@phosphor-icons/react';
import { projectService, duplicateService } from '../../services/api';
import './DuplicatesView.css';

const DuplicatesView = () => {
  const navigate = useNavigate();
  const [projectId, setProjectId] = useState(null);
  const [groups, setGroups] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Try to find the latest project
  useEffect(() => {
    const initProject = async () => {
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
        setIsLoading(false);
      }
    };
    initProject();
  }, [navigate]);

  useEffect(() => {
    if (!projectId) return;

    const fetchDuplicates = async () => {
      setIsLoading(true);
      try {
        const data = await duplicateService.getGroups(projectId);
        setGroups(data);
      } catch (error) {
        console.error('Error fetching duplicate groups:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDuplicates();
  }, [projectId]);

  const handlePhotoClick = (id) => {
    navigate(`/photos/${id}`);
  };

  return (
    <div className="duplicates-view">
      <div className="duplicates-header">
        <h2>Duplicate Groups</h2>
        <p className="subtitle">
          Photos are grouped by visual similarity. The system penalizes duplicates to favor keeping only the best shot.
        </p>
      </div>

      {isLoading ? (
        <div className="duplicates-loading">Loading duplicate groups...</div>
      ) : groups.length === 0 ? (
        <div className="duplicates-empty">
          <Copy size={48} className="empty-icon" />
          <h3>No Duplicates Found</h3>
          <p>No similar or exact duplicate photos were detected in this project.</p>
        </div>
      ) : (
        <div className="groups-container">
          {groups.map((group, index) => (
            <div key={group.group_id} className="card group-card">
              <div className="group-header">
                <div className="group-title">
                  <span className="group-number">Group {index + 1}</span>
                  <span className="group-badge">
                    {group.group_type === 'exact' ? 'Exact Matches' : 'Similar Photos'}
                  </span>
                </div>
                <div className="group-stats">
                  {group.member_count} photos
                </div>
              </div>

              <div className="group-photos">
                {group.photos.map(photo => (
                  <div 
                    key={photo.id} 
                    className={`group-photo-card category-${photo.category}`}
                    onClick={() => handlePhotoClick(photo.id)}
                  >
                    <div className="group-photo-thumbnail">
                      {photo.thumbnail_url ? (
                        <img src={`http://localhost:8000${photo.thumbnail_url}`} alt={photo.filename} loading="lazy" />
                      ) : (
                        <div className="photo-placeholder">No Image</div>
                      )}
                      <div className={`photo-badge badge-${photo.category}`}>
                        {photo.category}
                      </div>
                    </div>
                    <div className="group-photo-info">
                      <div className="group-photo-filename" title={photo.filename}>
                        {photo.filename}
                      </div>
                      <div className="group-photo-score">
                        Score: {photo.quality_score ? photo.quality_score.toFixed(1) : 'N/A'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DuplicatesView;

import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Funnel, WarningCircle } from '@phosphor-icons/react';
import { projectService, photoService } from '../../services/api';
import './ResultsView.css';

const ResultsView = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const projectIdStr = searchParams.get('projectId');
  const initialCategory = searchParams.get('category') || 'all';

  const [projectId, setProjectId] = useState(projectIdStr ? parseInt(projectIdStr) : null);
  const [photos, setPhotos] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState(initialCategory);
  
  // Try to find the latest project if none is specified
  useEffect(() => {
    const initProject = async () => {
      if (!projectId) {
        try {
          const projects = await projectService.getProjects();
          if (projects && projects.length > 0) {
            setProjectId(projects[0].id);
          } else {
            navigate('/import');
          }
        } catch (error) {
          console.error('Error fetching projects:', error);
          setIsLoading(false);
        }
      }
    };
    initProject();
  }, [projectId, navigate]);

  useEffect(() => {
    if (!projectId) return;

    const fetchPhotos = async () => {
      setIsLoading(true);
      try {
        const page = parseInt(searchParams.get('page') || '1');
        const params = { page, per_page: 50 };
        
        if (categoryFilter !== 'all') {
          params.category = categoryFilter;
        }
        
        const data = await photoService.getPhotos(projectId, params);
        setPhotos(data.data);
        setPagination(data.pagination);
      } catch (error) {
        console.error('Error fetching photos:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPhotos();
  }, [projectId, categoryFilter, searchParams]);

  const handleCategoryChange = (e) => {
    const newCategory = e.target.value;
    setCategoryFilter(newCategory);
    
    // Update URL params
    const newParams = new URLSearchParams(searchParams);
    if (newCategory === 'all') {
      newParams.delete('category');
    } else {
      newParams.set('category', newCategory);
    }
    newParams.set('page', '1'); // Reset to page 1 on filter change
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
  };

  const handlePhotoClick = (id) => {
    navigate(`/photos/${id}`);
  };

  return (
    <div className="results-view">
      <div className="results-header">
        <h2>Photo Results</h2>
        <div className="filter-controls">
          <Funnel size={20} />
          <select 
            className="input category-select" 
            value={categoryFilter}
            onChange={handleCategoryChange}
          >
            <option value="all">All Categories</option>
            <option value="good">Good</option>
            <option value="review">Review</option>
            <option value="poor">Poor</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="results-loading">Loading photos...</div>
      ) : photos.length === 0 ? (
        <div className="results-empty">
          <WarningCircle size={48} />
          <h3>No photos found</h3>
          <p>Try changing your filter criteria.</p>
        </div>
      ) : (
        <>
          <div className="photo-grid">
            {photos.map(photo => (
              <div 
                key={photo.id} 
                className={`photo-card category-${photo.category}`}
                onClick={() => handlePhotoClick(photo.id)}
              >
                <div className="photo-thumbnail">
                  {photo.thumbnail_url ? (
                    <img src={`http://localhost:8000${photo.thumbnail_url}`} alt={photo.filename} loading="lazy" />
                  ) : (
                    <div className="photo-placeholder">No Image</div>
                  )}
                  <div className={`photo-badge badge-${photo.category}`}>
                    {photo.category}
                  </div>
                </div>
                <div className="photo-info">
                  <div className="photo-filename" title={photo.filename}>
                    {photo.filename}
                  </div>
                  <div className="photo-score">
                    Score: {photo.quality_score ? photo.quality_score.toFixed(1) : 'N/A'}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {pagination && pagination.total_pages > 1 && (
            <div className="pagination">
              <button 
                className="btn btn-secondary" 
                disabled={pagination.page <= 1}
                onClick={() => handlePageChange(pagination.page - 1)}
              >
                Previous
              </button>
              <span className="page-info">
                Page {pagination.page} of {pagination.total_pages}
              </span>
              <button 
                className="btn btn-secondary" 
                disabled={pagination.page >= pagination.total_pages}
                onClick={() => handlePageChange(pagination.page + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ResultsView;

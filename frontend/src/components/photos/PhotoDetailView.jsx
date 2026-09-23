import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  CheckCircle, 
  MagnifyingGlass, 
  XCircle,
  Warning,
  Info
} from '@phosphor-icons/react';
import { photoService } from '../../services/api';
import './PhotoDetailView.css';

const PhotoDetailView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [photo, setPhoto] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    const fetchPhoto = async () => {
      try {
        const data = await photoService.getPhotoDetail(id);
        setPhoto(data);
      } catch (error) {
        console.error("Failed to fetch photo details:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchPhoto();
  }, [id]);

  const handleCategoryChange = async (newCategory) => {
    if (photo.analysis.category === newCategory) return;
    
    setIsUpdating(true);
    try {
      await photoService.updateCategory(id, newCategory);
      setPhoto({
        ...photo,
        analysis: {
          ...photo.analysis,
          category: newCategory,
          is_manually_modified: true
        }
      });
    } catch (error) {
      console.error("Failed to update category:", error);
      alert("Failed to update category");
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return <div className="photo-detail-loading">Loading photo details...</div>;
  }

  if (!photo) {
    return <div className="photo-detail-error">Photo not found.</div>;
  }

  const { analysis } = photo;
  const currentCategory = analysis ? analysis.category : 'pending';

  return (
    <div className="photo-detail-view">
      <div className="detail-header">
        <button className="btn btn-icon" onClick={() => navigate(-1)}>
          <ArrowLeft size={20} />
          <span>Back</span>
        </button>
        <div className="filename">{photo.filename}</div>
      </div>

      <div className="detail-content">
        <div className="main-preview">
          {photo.preview_url ? (
            <img 
              src={`http://localhost:8000${photo.preview_url}`} 
              alt={photo.filename} 
              className={`preview-image border-${currentCategory}`}
            />
          ) : (
            <div className="preview-placeholder">Preview not available</div>
          )}
          
          <div className="manual-override">
            <h4>Category</h4>
            <div className="category-buttons">
              <button 
                className={`btn category-btn btn-good ${currentCategory === 'good' ? 'active' : ''}`}
                onClick={() => handleCategoryChange('good')}
                disabled={isUpdating}
              >
                <CheckCircle size={20} /> Good
              </button>
              <button 
                className={`btn category-btn btn-review ${currentCategory === 'review' ? 'active' : ''}`}
                onClick={() => handleCategoryChange('review')}
                disabled={isUpdating}
              >
                <MagnifyingGlass size={20} /> Review
              </button>
              <button 
                className={`btn category-btn btn-poor ${currentCategory === 'poor' ? 'active' : ''}`}
                onClick={() => handleCategoryChange('poor')}
                disabled={isUpdating}
              >
                <XCircle size={20} /> Poor
              </button>
            </div>
            {analysis?.is_manually_modified && (
              <div className="manual-flag">
                <Info size={16} /> Manually Overridden
              </div>
            )}
          </div>
        </div>

        <div className="analysis-sidebar">
          {photo.detected_issues && photo.detected_issues.length > 0 && (
            <div className="card issues-card">
              <h3>Detected Issues</h3>
              <ul className="issues-list">
                {photo.detected_issues.map((issue, idx) => (
                  <li key={idx}>
                    <Warning size={16} className="warning-icon" />
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="card metrics-card">
            <h3>Analysis Metrics</h3>
            
            <div className="metric-group">
              <div className="metric-header">
                <span>Quality Score</span>
                <span className="metric-value highlight">{analysis?.quality_score?.toFixed(1) || 'N/A'}/100</span>
              </div>
            </div>

            <div className="metric-group">
              <div className="metric-header">
                <span>Sharpness</span>
                <span className="metric-value">{analysis?.blur_status}</span>
              </div>
              <div className="metric-detail">Variance: {analysis?.sharpness_score?.toFixed(0) || 'N/A'}</div>
            </div>

            <div className="metric-group">
              <div className="metric-header">
                <span>Exposure</span>
                <span className="metric-value">{analysis?.exposure_status}</span>
              </div>
              <div className="metric-detail">Brightness: {analysis?.brightness_avg?.toFixed(1) || 'N/A'}</div>
            </div>

            <div className="metric-group">
              <div className="metric-header">
                <span>Faces</span>
                <span className="metric-value">{analysis?.face_count || 0}</span>
              </div>
              {analysis?.closed_eye_detected && (
                <div className="metric-detail warning-text">Closed eyes detected</div>
              )}
            </div>
          </div>

          <div className="card metadata-card">
            <h3>File Metadata</h3>
            <div className="meta-row">
              <span className="meta-label">Dimensions</span>
              <span className="meta-value">{photo.width} × {photo.height}</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Resolution</span>
              <span className="meta-value">{photo.megapixels?.toFixed(1)} MP</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Size</span>
              <span className="meta-value">{(photo.file_size / (1024 * 1024)).toFixed(2)} MB</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Format</span>
              <span className="meta-value">{photo.format}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PhotoDetailView;

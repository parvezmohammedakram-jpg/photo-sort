import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ImportView from './components/import/ImportView';
import ProcessingView from './components/processing/ProcessingView';
import Dashboard from './components/dashboard/Dashboard';
import ResultsView from './components/photos/ResultsView';
import PhotoDetailView from './components/photos/PhotoDetailView';
import DuplicatesView from './components/duplicates/DuplicatesView';
import ExportView from './components/export/ExportView';
import ProjectsView from './components/projects/ProjectsView';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="projects" element={<ProjectsView />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="import" element={<ImportView />} />
          <Route path="processing" element={<ProcessingView />} />
          <Route path="results" element={<ResultsView />} />
          <Route path="review" element={<ResultsView isReviewMode={true} />} />
          <Route path="photos/:id" element={<PhotoDetailView />} />
          <Route path="duplicates" element={<DuplicatesView />} />
          <Route path="export" element={<ExportView />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

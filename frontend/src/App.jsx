import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';

// Placeholder components
const Dashboard = () => <div><h2>Dashboard</h2><p>Overview statistics will appear here.</p></div>;
const ImportView = () => <div><h2>Import</h2><p>Import photos here.</p></div>;
const ProcessingView = () => <div><h2>Processing</h2><p>Processing progress here.</p></div>;
const ResultsView = () => <div><h2>Results</h2><p>Photo grid results here.</p></div>;
const DuplicatesView = () => <div><h2>Duplicates</h2><p>Duplicate groups here.</p></div>;
const ExportView = () => <div><h2>Export</h2><p>Export options here.</p></div>;

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="import" element={<ImportView />} />
          <Route path="processing" element={<ProcessingView />} />
          <Route path="results" element={<ResultsView />} />
          <Route path="duplicates" element={<DuplicatesView />} />
          <Route path="export" element={<ExportView />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

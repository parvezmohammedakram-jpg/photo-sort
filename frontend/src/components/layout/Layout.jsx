import { NavLink, Outlet } from 'react-router-dom';
import { 
  SquaresFour, 
  UploadSimple, 
  Image, 
  Copy, 
  Export, 
  Spinner,
  MagnifyingGlass,
  FolderOpen
} from '@phosphor-icons/react';
import './Layout.css';

const navItems = [
  { path: '/projects', label: 'Projects', icon: <FolderOpen size={20} /> },
  { path: '/dashboard', label: 'Dashboard', icon: <SquaresFour size={20} /> },
  { path: '/import', label: 'Import', icon: <UploadSimple size={20} /> },
  { path: '/processing', label: 'Processing', icon: <Spinner size={20} /> },
  { path: '/results', label: 'Results', icon: <Image size={20} /> },
  { path: '/review', label: 'Review', icon: <MagnifyingGlass size={20} /> },
  { path: '/duplicates', label: 'Duplicates', icon: <Copy size={20} /> },
  { path: '/export', label: 'Export', icon: <Export size={20} /> },
];

const Layout = () => {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">PhotoSort</h1>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-item ${isActive ? 'active' : ''}`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;

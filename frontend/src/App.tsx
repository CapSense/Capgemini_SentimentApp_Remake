import WebApp from './components/WebApp';
import './WebApp.css';
import axios from 'axios';

function App() {
  const handleDashboardAccess = () => {
    axios.get('http://localhost:5000/export-results')
      .then(() => console.log('Dashboard endpoint hit'))
      .catch(err => console.error('Dashboard access failed:', err));
  };

  return (
    <div className="web-app bg-beige min-vh-100">
      <div className="topbar d-flex justify-content-between align-items-center px-4 py-3 mb-4">
        <h1 className="fw-bold m-0">CapSense AI</h1>
        <div className="header-icons">
          <button className="btn btn-outline-dark" onClick={handleDashboardAccess}>Dashboard</button>
          <button className="btn btn-outline-secondary">⚙</button>
        </div>
      </div>
      <WebApp />
    </div>
  );
}

export default App;

import WebApp from './components/WebApp';
import './WebApp.css';
import axios from 'axios';
import { useState } from 'react';

function App() {
  const [dashboardData, setDashboardData] = useState<any[]>([]);
  const [dashboardLoading, setDashboardLoading] = useState<boolean>(false);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [showDashboard, setShowDashboard] = useState<boolean>(false);

  const handleDashboardAccess = async () => {
    setDashboardLoading(true);
    setDashboardError(null);
    
    try {
      const response = await axios.get('/api/dashboard');
      setDashboardData(response.data);
      setShowDashboard(true);
      setDashboardLoading(false);
    } catch (err) {
      console.error('Dashboard access failed:', err);
      setDashboardError('Failed to load dashboard data. Please try again.');
      setDashboardLoading(false);
    }
  };

  const closeDashboard = () => {
    setShowDashboard(false);
  };

  return (
    <div style={{width: '100%', maxWidth: '100%', padding: 0, margin: 0}}>
      <div className="topbar d-flex justify-content-between align-items-center px-4 py-3">
        <h1 className="fw-bold m-0">CapSense AI</h1>
        <div className="header-icons">
          <button 
            className="btn btn-dark"
            onClick={handleDashboardAccess}
            disabled={dashboardLoading}
          >
            Dashboard
          </button>
          <button className="btn btn-secondary">?</button>
        </div>
      </div>
      
      {/* Dashboard Modal */}
      {showDashboard && (
        <div className="modal show d-block" tabIndex={-1} role="dialog">
          <div className="modal-dialog modal-lg" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Feedback Dashboard</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={closeDashboard}
                  aria-label="Close"
                />
              </div>
              <div className="modal-body">
                {dashboardError ? (
                  <div className="alert alert-danger">{dashboardError}</div>
                ) : dashboardData.length > 0 ? (
                  <div className="table-responsive">
                    <table className="table table-striped">
                      <thead>
                        <tr>
                          <th>Customer Text</th>
                          <th>Sentiment</th>
                          <th>AI Response</th>
                          <th>Empathy Score</th>
                          <th>Sarcasm</th>
                          <th>Emotion</th>
                          <th>Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dashboardData.map((item, index) => (
                          <tr key={index}>
                            <td>{item.customer_text.substring(0, 50)}...</td>
                            <td>{item.sentiment}</td>
                            <td>{item.response_text.substring(0, 50)}...</td>
                            <td>{item.empathy_score}</td>
                            <td>{item.sarcasm_detected ? 'Yes' : 'No'}</td>
                            <td>{item.emotion}</td>
                            <td>{new Date(item.created_at).toLocaleDateString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p>No data available in the dashboard.</p>
                )}
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={closeDashboard}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Main application */}
      <div className="web-app" style={{width: '100%', maxWidth: '100%'}}>
        <WebApp />
      </div>
    </div>
  );
}

export default App;
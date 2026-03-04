import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // We start by assuming it's checking, instead of hardcoding "Offline"
  const [status, setStatus] = useState("Checking...");

  // useEffect runs once when the component first loads
  useEffect(() => {
    // We reach out to the Python backend's /status URL
    fetch("http://127.0.0.1:8000/status")
      .then(response => response.json())
      .then(data => {
        // If successful, we update our status with the word "Online" from Python
        setStatus(data.status);
      })
      .catch(error => {
        // If it fails (like if you closed the Python terminal), it shows this
        setStatus("Offline (Backend unreachable)");
      });
  }, []);

  return (
    <div className="app-container">
      <h1>Satu Ai</h1>
      <p>System Initializing...</p>

      <div className="status-box">
        {/* We use the dynamic status variable here instead of typed text */}
        <p>Status: {status}</p>
      </div>
    </div>
  )
}

export default App
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Wifi, Radio, Shield, Target, Key, Activity, 
  Terminal, Search, Zap, Lock, RefreshCw, AlertCircle,
  Check, X, Download, Upload, ChevronRight
} from 'lucide-react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [adapters, setAdapters] = useState([]);
  const [selectedAdapter, setSelectedAdapter] = useState('');
  const [networks, setNetworks] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);
  const [selectedNetwork, setSelectedNetwork] = useState(null);

  // Attack parameters
  const [deauthParams, setDeauthParams] = useState({
    targetBssid: '',
    targetClient: '',
    packets: 50
  });

  const [handshakeParams, setHandshakeParams] = useState({
    targetBssid: '',
    channel: 6,
    duration: 60,
    useDeauth: false
  });

  useEffect(() => {
    loadAdapters();
  }, []);

  const showMessage = (text, type = 'info') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const loadAdapters = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/adapter/list`);
      if (response.data.success) {
        setAdapters(response.data.adapters);
        if (response.data.adapters.length > 0) {
          setSelectedAdapter(response.data.adapters[0].interface);
        }
      }
    } catch (error) {
      showMessage('Failed to load adapters: ' + error.message, 'error');
    }
  };

  const enableMonitorMode = async () => {
    if (!selectedAdapter) return;
    setLoading(true);
    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/adapter/monitor/enable/${selectedAdapter}`
      );
      showMessage(response.data.message, 'success');
      await loadAdapters();
    } catch (error) {
      showMessage('Failed to enable monitor mode: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const disableMonitorMode = async () => {
    if (!selectedAdapter) return;
    setLoading(true);
    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/adapter/monitor/disable/${selectedAdapter}`
      );
      showMessage(response.data.message, 'success');
      await loadAdapters();
    } catch (error) {
      showMessage('Failed to disable monitor mode: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const scanNetworks = async () => {
    if (!selectedAdapter) {
      showMessage('Please select an adapter', 'error');
      return;
    }
    
    setScanning(true);
    setNetworks([]);
    showMessage('Scanning for networks...', 'info');
    
    try {
      const response = await axios.post(`${BACKEND_URL}/api/scan/start`, {
        interface: selectedAdapter,
        duration: 10
      });
      
      if (response.data.success) {
        setNetworks(response.data.networks);
        showMessage(`Found ${response.data.total} networks`, 'success');
        loadScanHistory();
      }
    } catch (error) {
      showMessage('Scan failed: ' + error.message, 'error');
    } finally {
      setScanning(false);
    }
  };

  const loadScanHistory = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/scan/history?limit=5`);
      if (response.data.success) {
        setScanHistory(response.data.scans);
      }
    } catch (error) {
      console.error('Failed to load scan history:', error);
    }
  };

  const executeDeauth = async () => {
    if (!selectedAdapter || !deauthParams.targetBssid) {
      showMessage('Please provide required parameters', 'error');
      return;
    }

    setLoading(true);
    showMessage('Executing deauth attack...', 'info');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/attack/deauth`, {
        interface: selectedAdapter,
        target_bssid: deauthParams.targetBssid,
        target_client: deauthParams.targetClient || null,
        packets: parseInt(deauthParams.packets)
      });

      if (response.data.success) {
        showMessage('Deauth attack completed successfully', 'success');
      } else {
        showMessage('Deauth attack failed', 'error');
      }
    } catch (error) {
      showMessage('Deauth attack error: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const captureHandshake = async () => {
    if (!selectedAdapter || !handshakeParams.targetBssid) {
      showMessage('Please provide required parameters', 'error');
      return;
    }

    setLoading(true);
    showMessage('Capturing handshake...', 'info');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/capture/handshake`, {
        interface: selectedAdapter,
        target_bssid: handshakeParams.targetBssid,
        channel: parseInt(handshakeParams.channel),
        duration: parseInt(handshakeParams.duration)
      });

      if (response.data.success) {
        showMessage('Handshake captured successfully!', 'success');
      } else {
        showMessage(response.data.result?.message || 'Handshake capture failed', 'warning');
      }
    } catch (error) {
      showMessage('Handshake capture error: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const selectNetworkForAttack = (network) => {
    setSelectedNetwork(network);
    setDeauthParams({
      ...deauthParams,
      targetBssid: network.bssid
    });
    setHandshakeParams({
      ...handshakeParams,
      targetBssid: network.bssid,
      channel: parseInt(network.channel) || 6
    });
  };

  return (
    <div className="app" data-testid="wifi-tool-app">
      {/* Header */}
      <header className="header" data-testid="app-header">
        <div className="header-content">
          <div className="logo">
            <Shield className="logo-icon" />
            <div>
              <h1>WiFi Red Team Tool</h1>
              <p>All-in-One WiFi Security Testing Platform</p>
            </div>
          </div>
          <div className="header-actions">
            <button 
              onClick={loadAdapters} 
              className="btn-icon"
              data-testid="refresh-adapters-btn"
            >
              <RefreshCw size={18} />
            </button>
          </div>
        </div>
      </header>

      {/* Message Bar */}
      {message && (
        <div className={`message message-${message.type}`} data-testid="message-bar">
          {message.type === 'success' && <Check size={18} />}
          {message.type === 'error' && <X size={18} />}
          {message.type === 'info' && <AlertCircle size={18} />}
          {message.type === 'warning' && <AlertCircle size={18} />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Navigation */}
      <nav className="nav" data-testid="main-nav">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''} 
          onClick={() => setActiveTab('dashboard')}
          data-testid="tab-dashboard"
        >
          <Activity size={18} />
          Dashboard
        </button>
        <button 
          className={activeTab === 'scanner' ? 'active' : ''} 
          onClick={() => setActiveTab('scanner')}
          data-testid="tab-scanner"
        >
          <Search size={18} />
          Scanner
        </button>
        <button 
          className={activeTab === 'attacks' ? 'active' : ''} 
          onClick={() => setActiveTab('attacks')}
          data-testid="tab-attacks"
        >
          <Zap size={18} />
          Attacks
        </button>
        <button 
          className={activeTab === 'handshake' ? 'active' : ''} 
          onClick={() => setActiveTab('handshake')}
          data-testid="tab-handshake"
        >
          <Target size={18} />
          Handshake
        </button>
        <button 
          className={activeTab === 'cracking' ? 'active' : ''} 
          onClick={() => setActiveTab('cracking')}
          data-testid="tab-cracking"
        >
          <Key size={18} />
          Cracking
        </button>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="tab-content" data-testid="dashboard-tab">
            <h2 className="tab-title">
              <Activity size={24} />
              Dashboard
            </h2>

            <div className="grid-2">
              {/* Adapter Management */}
              <div className="card">
                <h3><Radio size={20} /> WiFi Adapters</h3>
                {adapters.length === 0 ? (
                  <div className="empty-state">
                    <Wifi size={48} />
                    <p>No WiFi adapters found</p>
                    <button onClick={loadAdapters} className="btn-primary">
                      Refresh
                    </button>
                  </div>
                ) : (
                  <>
                    <select 
                      value={selectedAdapter} 
                      onChange={(e) => setSelectedAdapter(e.target.value)}
                      className="select"
                      data-testid="adapter-select"
                    >
                      {adapters.map(adapter => (
                        <option key={adapter.interface} value={adapter.interface}>
                          {adapter.interface} ({adapter.mode})
                        </option>
                      ))}
                    </select>

                    {selectedAdapter && (
                      <div className="adapter-info">
                        {adapters.find(a => a.interface === selectedAdapter) && (
                          <>
                            <div className="info-row">
                              <span>Mode:</span>
                              <span className="badge">
                                {adapters.find(a => a.interface === selectedAdapter).mode}
                              </span>
                            </div>
                            <div className="info-row">
                              <span>Status:</span>
                              <span className={`status-badge status-${adapters.find(a => a.interface === selectedAdapter).status.toLowerCase()}`}>
                                {adapters.find(a => a.interface === selectedAdapter).status}
                              </span>
                            </div>
                          </>
                        )}
                      </div>
                    )}

                    <div className="button-group">
                      <button 
                        onClick={enableMonitorMode} 
                        className="btn-primary"
                        disabled={loading}
                        data-testid="enable-monitor-btn"
                      >
                        Enable Monitor Mode
                      </button>
                      <button 
                        onClick={disableMonitorMode} 
                        className="btn-secondary"
                        disabled={loading}
                        data-testid="disable-monitor-btn"
                      >
                        Disable Monitor Mode
                      </button>
                    </div>
                  </>
                )}
              </div>

              {/* Quick Stats */}
              <div className="card">
                <h3><Activity size={20} /> Quick Stats</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <Wifi size={32} />
                    <div>
                      <div className="stat-value">{adapters.length}</div>
                      <div className="stat-label">Adapters</div>
                    </div>
                  </div>
                  <div className="stat-card">
                    <Search size={32} />
                    <div>
                      <div className="stat-value">{networks.length}</div>
                      <div className="stat-label">Networks Found</div>
                    </div>
                  </div>
                  <div className="stat-card">
                    <Target size={32} />
                    <div>
                      <div className="stat-value">{scanHistory.length}</div>
                      <div className="stat-label">Total Scans</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Scans */}
            {scanHistory.length > 0 && (
              <div className="card">
                <h3><Terminal size={20} /> Recent Scans</h3>
                <div className="scan-history">
                  {scanHistory.map((scan, idx) => (
                    <div key={idx} className="scan-item">
                      <div>
                        <strong>{scan.scan_id}</strong>
                        <span className="text-muted">{scan.interface}</span>
                      </div>
                      <div>
                        <span className="badge">{scan.total_networks} networks</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Scanner Tab */}
        {activeTab === 'scanner' && (
          <div className="tab-content" data-testid="scanner-tab">
            <h2 className="tab-title">
              <Search size={24} />
              Network Scanner
            </h2>

            <div className="card">
              <div className="scan-controls">
                <select 
                  value={selectedAdapter} 
                  onChange={(e) => setSelectedAdapter(e.target.value)}
                  className="select"
                  disabled={scanning}
                  data-testid="scanner-adapter-select"
                >
                  <option value="">Select Adapter</option>
                  {adapters.map(adapter => (
                    <option key={adapter.interface} value={adapter.interface}>
                      {adapter.interface}
                    </option>
                  ))}
                </select>

                <button 
                  onClick={scanNetworks} 
                  className="btn-primary"
                  disabled={!selectedAdapter || scanning}
                  data-testid="start-scan-btn"
                >
                  {scanning ? (
                    <>
                      <RefreshCw className="spinning" size={18} />
                      Scanning...
                    </>
                  ) : (
                    <>
                      <Search size={18} />
                      Start Scan
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Networks List */}
            {networks.length > 0 && (
              <div className="networks-grid">
                {networks.map((network, idx) => (
                  <div 
                    key={idx} 
                    className={`network-card ${selectedNetwork?.bssid === network.bssid ? 'selected' : ''}`}
                    onClick={() => selectNetworkForAttack(network)}
                    data-testid={`network-card-${idx}`}
                  >
                    <div className="network-header">
                      <h4>{network.essid || 'Hidden Network'}</h4>
                      <span className={`encryption-badge encryption-${(network.privacy || network.encryption || 'open').toLowerCase()}`}>
                        {network.privacy || network.encryption || 'Open'}
                      </span>
                    </div>
                    <div className="network-details">
                      <div className="detail-row">
                        <span>BSSID:</span>
                        <code>{network.bssid}</code>
                      </div>
                      <div className="detail-row">
                        <span>Channel:</span>
                        <strong>{network.channel}</strong>
                      </div>
                      <div className="detail-row">
                        <span>Signal:</span>
                        <strong>{network.power} dBm</strong>
                      </div>
                    </div>
                    <button className="btn-sm-primary" data-testid={`select-network-${idx}`}>
                      <ChevronRight size={16} />
                      Select for Attack
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Attacks Tab */}
        {activeTab === 'attacks' && (
          <div className="tab-content" data-testid="attacks-tab">
            <h2 className="tab-title">
              <Zap size={24} />
              Attack Modules
            </h2>

            <div className="card">
              <h3><Zap size={20} /> Deauthentication Attack</h3>
              <p className="text-muted">
                Disconnect clients from a target access point by sending deauthentication packets.
              </p>

              <div className="form-group">
                <label>Target BSSID</label>
                <input
                  type="text"
                  value={deauthParams.targetBssid}
                  onChange={(e) => setDeauthParams({...deauthParams, targetBssid: e.target.value})}
                  placeholder="00:11:22:33:44:55"
                  className="input"
                  data-testid="deauth-bssid-input"
                />
              </div>

              <div className="form-group">
                <label>Target Client MAC (Optional - Broadcast if empty)</label>
                <input
                  type="text"
                  value={deauthParams.targetClient}
                  onChange={(e) => setDeauthParams({...deauthParams, targetClient: e.target.value})}
                  placeholder="AA:BB:CC:DD:EE:FF"
                  className="input"
                  data-testid="deauth-client-input"
                />
              </div>

              <div className="form-group">
                <label>Number of Packets</label>
                <input
                  type="number"
                  value={deauthParams.packets}
                  onChange={(e) => setDeauthParams({...deauthParams, packets: e.target.value})}
                  className="input"
                  min="1"
                  max="1000"
                  data-testid="deauth-packets-input"
                />
              </div>

              <button 
                onClick={executeDeauth} 
                className="btn-danger"
                disabled={loading || !deauthParams.targetBssid}
                data-testid="execute-deauth-btn"
              >
                <Zap size={18} />
                Execute Deauth Attack
              </button>
            </div>
          </div>
        )}

        {/* Handshake Tab */}
        {activeTab === 'handshake' && (
          <div className="tab-content" data-testid="handshake-tab">
            <h2 className="tab-title">
              <Target size={24} />
              Handshake Capture
            </h2>

            <div className="card">
              <h3><Target size={20} /> Capture WPA/WPA2 Handshake</h3>
              <p className="text-muted">
                Capture the 4-way handshake from a WPA/WPA2 protected network.
              </p>

              <div className="form-group">
                <label>Target BSSID</label>
                <input
                  type="text"
                  value={handshakeParams.targetBssid}
                  onChange={(e) => setHandshakeParams({...handshakeParams, targetBssid: e.target.value})}
                  placeholder="00:11:22:33:44:55"
                  className="input"
                  data-testid="handshake-bssid-input"
                />
              </div>

              <div className="grid-2">
                <div className="form-group">
                  <label>Channel</label>
                  <input
                    type="number"
                    value={handshakeParams.channel}
                    onChange={(e) => setHandshakeParams({...handshakeParams, channel: e.target.value})}
                    className="input"
                    min="1"
                    max="14"
                    data-testid="handshake-channel-input"
                  />
                </div>

                <div className="form-group">
                  <label>Duration (seconds)</label>
                  <input
                    type="number"
                    value={handshakeParams.duration}
                    onChange={(e) => setHandshakeParams({...handshakeParams, duration: e.target.value})}
                    className="input"
                    min="10"
                    max="300"
                    data-testid="handshake-duration-input"
                  />
                </div>
              </div>

              <div className="checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={handshakeParams.useDeauth}
                    onChange={(e) => setHandshakeParams({...handshakeParams, useDeauth: e.target.checked})}
                    data-testid="handshake-use-deauth-checkbox"
                  />
                  Send deauth packets to force handshake
                </label>
              </div>

              <button 
                onClick={captureHandshake} 
                className="btn-primary"
                disabled={loading || !handshakeParams.targetBssid}
                data-testid="capture-handshake-btn"
              >
                <Target size={18} />
                Capture Handshake
              </button>
            </div>
          </div>
        )}

        {/* Cracking Tab */}
        {activeTab === 'cracking' && (
          <div className="tab-content" data-testid="cracking-tab">
            <h2 className="tab-title">
              <Key size={24} />
              Password Cracking
            </h2>

            <div className="card">
              <h3><Lock size={20} /> Crack Captured Handshake</h3>
              <p className="text-muted">
                Use wordlist or brute force to crack captured WPA/WPA2 handshakes.
              </p>

              <div className="empty-state">
                <Key size={48} />
                <p>Password cracking interface coming soon</p>
                <small>Use CLI for now: <code>./cli/wifi_tool.py crack handshake [file] [wordlist]</code></small>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

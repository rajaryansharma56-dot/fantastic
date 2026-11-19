import Chatbot from "./Chatbot";
import "./Chatbot.css";
import { useState, useEffect } from "react";
import { getMachines, createMachine, getMachineRisks, getMaintenanceRecords } from "./api";
import {
  LayoutDashboard, Factory, Wrench, CalendarDays,
  Settings, Search, Bell, Plus, Activity,
  AlertTriangle, CheckCircle2, Clock,
  ChevronDown, ArrowUpRight, Gauge, X
} from "lucide-react";
import "./App.css";

function App() {
  const [machines, setMachines] = useState([]);
  const [maintenanceRecords, setMaintenanceRecords] = useState([]);
  const [riskAssessments, setRiskAssessments] = useState([]);
  const [riskError, setRiskError] = useState("");
  const [active, setActive] = useState("Overview");
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState({
    name: "", machine_code: "", location: ""
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      const results = await Promise.allSettled([
        getMachines(),
        getMaintenanceRecords(),
        getMachineRisks()
      ]);

      if (results[0].status === "fulfilled") {
        setMachines(results[0].value);
      } else {
        setError(results[0].reason.message);
      }

      if (results[1].status === "fulfilled") {
        setMaintenanceRecords(results[1].value);
      } else {
        setError(prev => prev || results[1].reason.message);
      }

      if (results[2].status === "fulfilled") {
        setRiskAssessments(
          results[2].value.risk_assessments || []
        );
        setRiskError("");
      } else {
        setRiskError(results[2].reason.message);
      }

      setLoading(false);
    }

    loadDashboard();
  }, []);
  const operational = machines.filter(
    m => m.status === "Operational"
  ).length;

  const maintenance = maintenanceRecords.filter(
    m => m.status === "In Progress"
  ).length;

  const warnings = riskAssessments.filter(
    r => ["HIGH", "CRITICAL"].includes(r.risk_level)
  ).length;

  const riskMap = new Map(
    riskAssessments.map(r => [r.machine_id, r])
  );

  const enrichedMachines = machines.map(machine => {
    const risk = riskMap.get(machine.id);

    return {
      ...machine,
      code: machine.machine_code,
      health:
        typeof risk?.risk_score === "number"
          ? Math.max(0, Math.min(100, 100 - risk.risk_score))
          : null
    };
  });

  const healthValues = enrichedMachines
    .map(m => m.health)
    .filter(value =>
      typeof value === "number" && Number.isFinite(value)
    );

  const averageHealth = healthValues.length
    ? Math.round(
        healthValues.reduce((a, b) => a + b, 0) /
        healthValues.length
      )
    : null;

  const filtered = enrichedMachines.filter(m =>
    `${m.name} ${m.code} ${m.location}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );
  async function addMachine(e) {
    e.preventDefault();
    setError("");

    try {
      await createMachine(form);

      const results = await Promise.allSettled([
        getMachines(),
        getMaintenanceRecords(),
        getMachineRisks()
      ]);

      if (results[0].status === "fulfilled") {
        setMachines(results[0].value);
      } else {
        setError(results[0].reason.message);
      }

      if (results[1].status === "fulfilled") {
        setMaintenanceRecords(results[1].value);
      }

      if (results[2].status === "fulfilled") {
        setRiskAssessments(
          results[2].value.risk_assessments || []
        );
        setRiskError("");
      } else {
        setRiskError(results[2].reason.message);
      }

      setForm({
        name: "",
        machine_code: "",
        location: ""
      });

      setShowForm(false);

    } catch (err) {
      setError(err.message);
    }
  }
  const navItems = [
    { name: "Overview", icon: LayoutDashboard },
    { name: "Machines", icon: Factory },
    { name: "Maintenance", icon: Wrench },
    { name: "Schedules", icon: CalendarDays },
  ];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><Activity size={23}/></div>
          <div>
            <h2>MAINTENA</h2>
            <span>INDUSTRIAL INTELLIGENCE</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>
        <nav>
          {navItems.map(item => (
            <button
              key={item.name}
              className={`nav-item ${active === item.name ? "active" : ""}`}
              onClick={() => setActive(item.name)}
            >
              <item.icon size={18}/>
              {item.name}
              {item.name === "Maintenance" && <span className="nav-count">{maintenance}</span>}
            </button>
          ))}
        </nav>

        <div className="nav-label management-label">SYSTEM</div>
        <button className="nav-item" onClick={() => setActive("Settings")}>
          <Settings size={18}/> Settings
        </button>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="live-dot"></span>
            <div><strong>System operational</strong><small>All services running</small></div>
          </div>
          <div className="profile">
            <div className="avatar">RA</div>
            <div><strong>Administrator</strong><small>Plant Manager</small></div>
            <ChevronDown size={16}/>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Workspace</span><span>/</span><strong>{active}</strong>
          </div>
          <div className="top-actions">
            <div className="environment"><span className="live-dot"></span> SYSTEM LIVE</div>
            <button className="icon-button" aria-label="Notifications"><Bell size={19}/><i/></button>
            <div className="top-avatar">RA</div>
          </div>
        </header>

        <section className="page-content">
          <div className="welcome-row">
            <div>
              <div className="eyebrow">INDUSTRIAL OPERATIONS / 2026</div>
              <h1>{active === "Overview" ? "Operations Overview" : active}</h1>
              <p>Monitor your assets and keep operations running smoothly.</p>
            </div>
            <button className="primary-button" onClick={() => setShowForm(true)}>
              <Plus size={17}/> Add Machine
            </button>
          </div>

          <div className="status-banner">
            <div className="banner-icon"><Activity size={20}/></div>
            <div><strong>Plant operations are being monitored</strong><p>Your asset overview is ready. Review machine health and upcoming maintenance.</p></div>
            <span className="banner-tag">LIVE MONITORING</span>
          </div>

          {error && (
            <div className="status-banner">
              <div className="banner-icon"><AlertTriangle size={20}/></div>
              <div><strong>Backend connection error</strong><p>{error}</p></div>
            </div>
          )}

          <div className="section-heading">
            <div><h3>Performance indicators</h3><p>Current asset status across your facility</p></div>
            <span className="updated"><span className="live-dot"/> LIVE DATA</span>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-top"><span>Total Machines</span><Factory size={19}/></div>
              <h2>{machines.length.toString().padStart(2, "0")}</h2>
              <div className="stat-foot">Registered assets</div>
            </div>
            <div className="stat-card">
              <div className="stat-top"><span>Operational</span><CheckCircle2 size={19}/></div>
              <h2>{operational.toString().padStart(2, "0")}</h2>
              <div className="stat-foot positive">Ã¢â€”Â Running normally</div>
            </div>
            <div className="stat-card">
              <div className="stat-top"><span>Under Maintenance</span><Wrench size={19}/></div>
              <h2>{maintenance.toString().padStart(2, "0")}</h2>
              <div className="stat-foot">Active maintenance</div>
            </div>
            <div className="stat-card">
              <div className="stat-top"><span>Attention Required</span><AlertTriangle size={19}/></div>
              <h2>{warnings.toString().padStart(2, "0")}</h2>
              <div className="stat-foot warning-text">Requires inspection</div>
            </div>
          </div>


          <section className="panel risk-panel">
            <div className="panel-header">
              <div>
                <h3>AI Machine Risk Assessment</h3>
                <p>Sensor-based equipment risk analysis</p>
              </div>
              <span className="updated"><span className="live-dot"/> RISK MONITORING</span>
            </div>

            {riskError && <p className="risk-error">{riskError}</p>}

            {!riskError && riskAssessments.length === 0 && (
              <p className="risk-empty">No risk assessments available.</p>
            )}

            <div className="risk-grid">
              {riskAssessments.map(item => {
                const level = (item.risk_level || "UNKNOWN").toLowerCase();
                const score = item.risk_score;

                return (
                  <div className="risk-card" key={item.machine_id}>
                    <div className="risk-card-top">
                      <div>
                        <h4>{item.machine_name}</h4>
                        <span>{item.machine_code}</span>
                      </div>
                      <span className={`risk-badge ${level}`}>
                        {item.risk_level}
                      </span>
                    </div>

                    <div className="risk-score-row">
                      <strong>{score !== null && score !== undefined ? score : "N/A"}</strong>
                      <span>/ 100 Risk Score</span>
                    </div>

                    <div className="risk-track">
                      <div
                        className={`risk-fill ${level}`}
                        style={{ width: `${Math.max(0, Math.min(100, Number(score) || 0))}%` }}
                      />
                    </div>

                    <div className="risk-coverage">
                      Data coverage <strong>{item.data_coverage}%</strong>
                    </div>

                    <div className="risk-reasons">
                      {item.reasons?.length > 0
                        ? item.reasons.map((reason, index) => (
                            <div key={index}>
                              <AlertTriangle size={13}/>
                              <span>{reason}</span>
                            </div>
                          ))
                        : <span>No risk factors detected.</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>

          <div className="content-grid">
            <section className="panel machine-panel">
              <div className="panel-header">
                <div><h3>Machine registry</h3><p>Manage and monitor registered equipment</p></div>
                <button className="text-button" onClick={() => setActive("Machines")}>View all <ArrowUpRight size={15}/></button>
              </div>
              <div className="table-tools">
                <div className="search-box"><Search size={16}/><input placeholder="Search machines..." value={search} onChange={e => setSearch(e.target.value)}/></div>
                <span className="record-count">{filtered.length} RECORDS</span>
              </div>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>MACHINE</th><th>LOCATION</th><th>EST. HEALTH</th><th>STATUS</th></tr></thead>
                  <tbody>
                    {loading && <tr><td colSpan="4" className="empty-row">Loading machines...</td></tr>}
                    {!loading && filtered.map(m => (
                      <tr key={m.id}>
                        <td><div className="machine-name">{m.name}</div><small className="machine-code">{m.code}</small></td>
                        <td>{m.location}</td>
                        <td>{typeof m.health === "number" && Number.isFinite(m.health) ? (<div className="health-cell"><div className="health-track"><div style={{width: `${m.health}%`}}/></div><span>{m.health}%</span></div>) : <span>N/A</span>}</td>
                        <td><span className={`status-pill ${m.status.toLowerCase()}`}>{m.status}</span></td>
                      </tr>
                    ))}
                    {!loading && filtered.length === 0 && <tr><td colSpan="4" className="empty-row">No machines found.</td></tr>}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="panel maintenance-panel">
              <div className="panel-header">
                <div><h3>Maintenance summary</h3><p>Facility maintenance overview</p></div>
                <Wrench size={19} className="muted-icon"/>
              </div>
              <div className="maintenance-feature">
                <div className="maintenance-circle"><Gauge size={27}/></div>
                <div><strong>{averageHealth !== null ? `${averageHealth}%` : "N/A"}</strong><span>Average estimated machine health</span></div>
              </div>
              <div className="summary-row"><span><i className="legend-dot green"/>Operational</span><strong>{operational}</strong></div>
              <div className="summary-row"><span><i className="legend-dot orange"/>Maintenance</span><strong>{maintenance}</strong></div>
              <div className="summary-row"><span><i className="legend-dot red"/>Attention required</span><strong>{warnings}</strong></div>
              <div className="maintenance-note"><Clock size={16}/><span>Review machine alerts regularly to prevent unexpected downtime.</span></div>
            </section>
          </div>

          <footer>MAINTENA <span>Ã¢â‚¬Â¢</span> INDUSTRIAL MAINTENANCE MANAGEMENT <span>Ã¢â‚¬Â¢</span> MVP VERSION 1.0</footer>
        </section>
      </main>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <form className="machine-form" onSubmit={addMachine} onClick={e => e.stopPropagation()}>
            <div className="modal-heading"><div><h2>Add new machine</h2><p>Register equipment in your facility</p></div><button type="button" className="icon-button" onClick={() => setShowForm(false)}><X size={19}/></button></div>
            <label>Machine name<input required value={form.name} onChange={e => setForm({...form,name:e.target.value})} placeholder="e.g. Industrial Motor"/></label>
            <label>Machine code<input required value={form.machine_code} onChange={e => setForm({...form,machine_code:e.target.value})} placeholder="e.g. MOT-006"/></label>
            <label>Location<input required value={form.location} onChange={e => setForm({...form,location:e.target.value})} placeholder="e.g. Factory Floor A"/></label>
            <button className="primary-button submit-button" type="submit">Register machine <Plus size={17}/></button>
          </form>
        </div>
      )}
      <Chatbot />
    </div>
  );
}

export default App;











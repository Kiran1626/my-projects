import { useEffect, useState } from "react";
import {
  getApplications,
  createApplication,
  updateApplication,
  deleteApplication,
  getStats,
  login,
  logout,
  isLoggedIn,
} from "./api.js";

const STATUSES = ["wishlist", "applied", "interview", "offer", "rejected"];
const PRIORITIES = ["low", "medium", "high"];

const EMPTY_FORM = {
  company: "",
  role: "",
  status: "wishlist",
  priority: "medium",
  source: "",
  salary: "",
  location: "",
  url: "",
  notes: "",
  applied_at: "",
};

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    try {
      await login(username, password);
      onLogin();
    } catch {
      setError("Invalid credentials.");
    }
  }

  return (
    <div className="login-wrap">
      <form className="card login" onSubmit={submit}>
        <h1>Job Application Tracker</h1>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="error">{error}</p>}
        <button type="submit">Sign in</button>
        <p className="hint">
          Create a user on the backend first:
          <br />
          <code>python manage.py createsuperuser</code>
        </p>
      </form>
    </div>
  );
}

function AppForm({ initial, onSave, onCancel }) {
  const [form, setForm] = useState(initial ? { ...EMPTY_FORM, ...initial, applied_at: initial.applied_at || "" } : EMPTY_FORM);

  function set(k, v) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  function submit(e) {
    e.preventDefault();
    const payload = { ...form, applied_at: form.applied_at || null };
    onSave(payload, initial?.id);
  }

  return (
    <form className="card form" onSubmit={submit}>
      <input required placeholder="Company" value={form.company} onChange={(e) => set("company", e.target.value)} />
      <input required placeholder="Role" value={form.role} onChange={(e) => set("role", e.target.value)} />
      <div className="row">
        <select value={form.status} onChange={(e) => set("status", e.target.value)}>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select value={form.priority} onChange={(e) => set("priority", e.target.value)}>
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <input type="date" value={form.applied_at || ""} onChange={(e) => set("applied_at", e.target.value)} />
      </div>
      <div className="row">
        <input placeholder="Location" value={form.location} onChange={(e) => set("location", e.target.value)} />
        <input placeholder="Salary" value={form.salary} onChange={(e) => set("salary", e.target.value)} />
        <input placeholder="Source" value={form.source} onChange={(e) => set("source", e.target.value)} />
      </div>
      <input placeholder="Job URL" value={form.url} onChange={(e) => set("url", e.target.value)} />
      <textarea placeholder="Notes" value={form.notes} onChange={(e) => set("notes", e.target.value)} />
      <div className="row">
        <button type="submit">Save</button>
        {onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

function Dashboard({ stats }) {
  if (!stats) return null;
  return (
    <div className="stats">
      <div className="card stat">
        <span className="num">{stats.total}</span>
        <span>Total</span>
      </div>
      {STATUSES.map((s) => (
        <div className="card stat" key={s}>
          <span className="num">{stats.by_status[s] || 0}</span>
          <span>{s}</span>
        </div>
      ))}
      <div className="card stat">
        <span className="num">{stats.interview_rate?.toFixed(0)}%</span>
        <span>interview rate</span>
      </div>
    </div>
  );
}

function App() {
  const [authed, setAuthed] = useState(isLoggedIn());
  const [apps, setApps] = useState([]);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState("all");
  const [stats, setStats] = useState(null);

  function load() {
    getApplications(filter === "all" ? {} : { status: filter })
      .then((r) => setApps(r.data.results ?? r.data))
      .catch(() => setAuthed(false));
    getStats()
      .then((r) => setStats(r.data))
      .catch(() => {});
  }

  useEffect(() => {
    if (authed) load();
  }, [authed, filter]);

  async function save(payload, id) {
    if (id) {
      await updateApplication(id, payload);
    } else {
      await createApplication(payload);
    }
    setShowForm(false);
    setEditing(null);
    load();
  }

  async function remove(id) {
    if (confirm("Delete this application?")) {
      await deleteApplication(id);
      load();
    }
  }

  function startEdit(app) {
    setEditing(app);
    setShowForm(true);
  }

  if (!authed) return <Login onLogin={() => setAuthed(true)} />;

  return (
    <div className="wrap">
      <header>
        <h1>Job Application Tracker</h1>
        <button
          className="secondary"
          onClick={() => {
            logout();
            setAuthed(false);
          }}
        >
          Log out
        </button>
      </header>

      <Dashboard stats={stats} />

      <div className="toolbar">
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button
          onClick={() => {
            setEditing(null);
            setShowForm((v) => !v);
          }}
        >
          {showForm && !editing ? "Close" : "+ New application"}
        </button>
      </div>

      {showForm && (
        <AppForm
          initial={editing}
          onSave={save}
          onCancel={() => {
            setShowForm(false);
            setEditing(null);
          }}
        />
      )}

      <div className="list">
        {apps.length === 0 && <p className="empty">No applications yet — add your first one!</p>}
        {apps.map((app) => (
          <div className="card app-row" key={app.id}>
            <div>
              <strong>{app.company}</strong>
              <span className="role"> — {app.role}</span>
              <div className="meta">
                {app.location && <span>📍 {app.location} · </span>}
                {app.salary && <span>💰 {app.salary} · </span>}
                <span className={`pill ${app.status}`}>{app.status}</span>
                <span className={`pill ${app.priority}`}>{app.priority}</span>
              </div>
              {app.notes && <p className="notes">{app.notes}</p>}
            </div>
            <div className="actions">
              <button onClick={() => startEdit(app)}>Edit</button>
              <button className="danger" onClick={() => remove(app.id)}>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

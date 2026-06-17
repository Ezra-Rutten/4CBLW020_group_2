// data.js — data layer for the dashboard.
// Real per-city data is fetched from the FastAPI backend (see backend/main.py).
// When served by uvicorn the page is same-origin so a relative URL works; when
// index.html is opened directly (file://) we fall back to the local API host
// (CORS is enabled on the backend for that case).
const API_BASE = location.protocol === 'file:' ? 'http://127.0.0.1:8000' : '';

// --- Backend fetchers --------------------------------------------------------
async function fetchCities(){
  const res = await fetch(`${API_BASE}/api/cities`);
  if (!res.ok) throw new Error(`GET /api/cities -> HTTP ${res.status}`);
  return res.json();
}

async function fetchCity(name){
  const res = await fetch(`${API_BASE}/api/city/${encodeURIComponent(name)}`);
  if (!res.ok) throw new Error(`GET /api/city/${name} -> HTTP ${res.status}`);
  const data = await res.json();
  // Normalize the numeric fields the frontend reads off each station. All
  // station "soft" signals (priority/allocation need) are now derived from the
  // real base_allocation_pct in app.js — no synthetic placeholders.
  data.stations = (data.stations || []).map(s => ({
    ...s,
    predicted_severity: Math.round(Number(s.predicted_severity ?? s.total_predicted_crime_severity ?? 0)),
    base_allocation_pct: Number(s.base_allocation_pct ?? s.budget_allocation_pct ?? 0)
  }));
  return data;
}

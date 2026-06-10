// data.js — data layer for the dashboard.
// Real per-city data is fetched from the FastAPI backend (see backend/main.py).
// When served by uvicorn the page is same-origin so a relative URL works; when
// index.html is opened directly (file://) we fall back to the local API host
// (CORS is enabled on the backend for that case).
const API_BASE = location.protocol === 'file:' ? 'http://127.0.0.1:8000' : '';

// --- Mock soft fields --------------------------------------------------------
// risk / pressure / forecast-trend are NOT produced by the backend yet. We
// synthesize stable placeholder values (deterministic per station name) so the
// existing widgets keep working. TODO: replace with real model output once those
// are implemented. (The old main_demand_profile was an invented specialist
// category not backed by crime_weight.py, so it has been removed.)
function mockSoftFields(name){
  let h = 0;
  for (let i = 0; i < name.length; i++) { h = (h * 31 + name.charCodeAt(i)) >>> 0; }
  const rnd = (h % 1000) / 1000;
  const pressure = +(1 + rnd * 3.5).toFixed(2);             // 1.00 .. 4.50
  const risk = pressure >= 3.5 ? 'Red' : pressure >= 2.2 ? 'Orange' : pressure >= 1.5 ? 'Yellow' : 'Green';
  return {
    pressure,
    risk,
    forecast_trend_pct: +(((h % 21) - 10) / 10).toFixed(1)   // -1.0 .. +1.0
  };
}

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
  // Normalize budget column name + attach mock soft fields to each station.
  data.stations = (data.stations || []).map(s => ({
    ...s,
    predicted_severity: Number(s.predicted_severity ?? s.total_predicted_crime_severity ?? 0),
    budget_allocation_pct: Number(s.budget_allocation_pct ?? s.base_allocation_pct ?? 0),
    ...mockSoftFields(String(s.station || ''))
  }));
  return data;
}

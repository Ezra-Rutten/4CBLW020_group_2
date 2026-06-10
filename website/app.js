// Each unit reads a backend % column carried on every station object (`field`).
// General police use base_allocation_pct (derived from the normal crime_weights
// via predicted severity); the specialists use their own demand-share columns
// (mental_health/social_services/negotiator/k9/swat). Each slider value is the
// TOTAL available headcount, split across stations by that backend share (%).
const resourceTypes=[
  {key:'general',        field:'base_allocation_pct', label:'General police officers',            short:'General', defaultValue:200},
  {key:'mental_health',  field:'mental_health',       label:'Mental-health / welfare specialists', short:'MH',      defaultValue:80},
  {key:'social_services',field:'social_services',     label:'Social-services / domestic support',  short:'Social',  defaultValue:50},
  {key:'negotiator',     field:'negotiator',          label:'Negotiators',                         short:'Negot',   defaultValue:20},
  {key:'k9',             field:'k9',                  label:'K9 units',                            short:'K9',      defaultValue:30},
  {key:'swat',           field:'swat',                label:'Armed / SWAT response units',         short:'SWAT',    defaultValue:25}
];
const riskOrder=['Red','Orange','Yellow','Green'];
const riskColors={Red:'#b91c1c',Orange:'#b45309',Yellow:'#a16207',Green:'#15803d'};
const MONTH_LABELS=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
let currentCity='London';
let currentCityData=null;   // payload for the selected city (fetched from backend)
const cityCache={};         // city name -> payload
let cityList=[];            // [{city, force, station_count, incident_estimate}]
let resources=Object.fromEntries(resourceTypes.map(r=>[r.key,r.defaultValue]));
const fmt=n=>Number(n||0).toLocaleString('en-GB');
const esc=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
function city(){return currentCityData}
function riskColor(r){return riskColors[r]||'#64748b'}
function riskClass(r){return riskOrder.includes(r)?r:'Green'}
function topStation(){return city()&&city().stations.length?[...city().stations].sort((a,b)=>b.pressure-a.pressure)[0]:null}
function maxPressure(){return Math.max(1,...city().stations.map(s=>Number(s.pressure)||0))}

async function loadCity(name){
  if(cityCache[name]){ currentCityData=cityCache[name]; return; }
  currentCityData=await fetchCity(name);
  cityCache[name]=currentCityData;
}

function showBackendError(err){
  console.error(err);
  const msg=`Could not reach the backend API (${err.message}). Start it with `+
            `"uvicorn main:app --port 8000" from the backend/ folder, then open http://localhost:8000/`;
  const m=document.getElementById('metrics');
  if(m) m.innerHTML=`<div class="metric"><small>Backend offline</small><b>${esc(msg)}</b></div>`;
  const b=document.getElementById('briefing');
  if(b) b.textContent=msg;
}

async function init(){
  // Build the dropdown from the backend's city list.
  try{
    cityList=await fetchCities();
  }catch(err){ showBackendError(err); return; }

  const sel=document.getElementById('citySelect');
  cityList.forEach(c=>{
    const option=document.createElement('option');
    option.value=c.city;
    option.textContent=c.city;
    sel.appendChild(option);
  });
  if(cityList.length && !cityList.some(c=>c.city===currentCity)) currentCity=cityList[0].city;
  sel.value=currentCity;

  sel.onchange=async e=>{
    currentCity=e.target.value;
    document.getElementById('searchBox').value='';
    document.getElementById('riskFilter').value='All';
    try{ await loadCity(currentCity); }catch(err){ showBackendError(err); return; }
    renderAll();
  };
  document.querySelectorAll('.tab').forEach(button=>{
    button.onclick=()=>{
      document.querySelectorAll('.tab').forEach(tab=>{
        tab.classList.remove('active');
        tab.setAttribute('aria-selected','false');
      });
      document.querySelectorAll('.panel').forEach(panel=>panel.classList.remove('active'));
      button.classList.add('active');
      button.setAttribute('aria-selected','true');
      document.getElementById(button.dataset.tab).classList.add('active');
    };
  });
  document.getElementById('searchBox').oninput=renderStations;
  document.getElementById('riskFilter').onchange=renderStations;
  renderResources();
  renderFolders();

  try{ await loadCity(currentCity); }catch(err){ showBackendError(err); return; }
  renderAll();
}

function renderAll(){
  renderMetrics();
  renderBriefing();
  renderMap();
  renderRecommendation();
  renderAllocationPanel();
  renderChart();
  renderTopCrimes();
  renderStations();
  renderFolderDetail();
}

function renderMetrics(){
  const c=city();
  const peak=topStation();
  document.getElementById('metrics').innerHTML=[
    ['Police force',c.force],
    ['Incident estimate',fmt(c.incident_estimate)],
    ['Stations in folder',c.stations.length],
    ['Peak pressure',peak?`${peak.pressure.toFixed(2)} - ${peak.station}`:'None']
  ].map(([label,value])=>`<div class="metric"><small>${esc(label)}</small><b title="${esc(value)}">${esc(value)}</b></div>`).join('');
}

function renderBriefing(){
  const c=city();
  const stations=c.stations;
  const counts=Object.fromEntries(riskOrder.map(r=>[r,stations.filter(s=>s.risk===r).length]));
  const total=Math.max(1,stations.length);
  document.getElementById('briefing').innerHTML=`${esc(c.note)}<br><br><span class="path">backend/data (force: ${esc(c.force)})</span>`;
  document.getElementById('riskSummary').innerHTML=[
    ['Red',counts.Red],
    ['Orange',counts.Orange],
    ['Peak',topStation()?topStation().pressure.toFixed(2):'0.00']
  ].map(([label,value])=>`<div class="risk-cell"><span class="meta-label">${esc(label)}</span><b>${esc(value)}</b></div>`).join('');
  document.getElementById('riskStrip').innerHTML=riskOrder.map(r=>{
    const width=counts[r]?Math.max(4,counts[r]/total*100):0;
    return `<span title="${r}: ${counts[r]}" style="width:${width}%;background:${riskColor(r)}"></span>`;
  }).join('');
}

function renderResources(){
  document.getElementById('resources').innerHTML=resourceTypes.map(item=>`
    <div class="resource">
      <label for="resource-${item.key}">${esc(item.label)}</label>
      <input id="resource-${item.key}" type="number" min="0" max="250" value="${resources[item.key]}" data-key="${item.key}">
      <input type="range" min="0" max="250" value="${resources[item.key]}" data-key="${item.key}" aria-label="${esc(item.label)}">
    </div>
  `).join('');
  document.querySelectorAll('#resources input').forEach(input=>{
    input.oninput=e=>{
      const key=e.target.dataset.key;
      const value=clamp(Number(e.target.value)||0,0,250);
      resources[key]=value;
      document.querySelectorAll(`#resources input[data-key="${key}"]`).forEach(pair=>{
        if(pair!==e.target) pair.value=value;
      });
      renderRecommendation();
      renderAllocationPanel();
      renderStations();
    };
  });
}

function stationAlloc(station){
  // Per-station headcount for each unit = backend share (%) * available input.
  // `field` is the station's % column for that unit (from the budget file).
  return Object.fromEntries(resourceTypes.map(({key,field})=>{
    const sharePct=Number(station[field])||0;
    return [key,Math.max(0,Math.round(sharePct/100*resources[key]))];
  }));
}

function focusList(station,limit=resourceTypes.length){
  const allocation=stationAlloc(station);
  return resourceTypes
    .map(item=>({label:item.short,value:allocation[item.key]}))
    .filter(item=>item.value>0)
    .sort((a,b)=>b.value-a.value)
    .slice(0,limit);
}

function renderRecommendation(){
  const top=topStation();
  if(!top){
    document.getElementById('recommendation').innerHTML='No station data available for this city.';
    return;
  }
  const focus=focusList(top,4).map(item=>`${esc(item.label)} ${fmt(item.value)}`).join(', ')||'No capacity set';
  document.getElementById('recommendation').innerHTML=`Highest-priority station: <b>${esc(top.station)}</b><br>Suggested focus: ${focus}.`;
}

function renderAllocationPanel(){
  const rows=[...city().stations].sort((a,b)=>b.pressure-a.pressure);
  document.getElementById('allocationPanel').innerHTML=rows.map(station=>{
    const chips=focusList(station).map(item=>`<span class="alloc-chip">${esc(item.label)} ${fmt(item.value)}</span>`).join('')||'<span class="alloc-chip">No capacity set</span>';
    return `<div class="alloc-row">
      <div>
        <div class="alloc-station">${esc(station.station)}</div>
        <div class="alloc-sub">${esc(station.postcode)} | predicted severity ${fmt(station.predicted_severity)}</div>
      </div>
      <div class="alloc-metrics">${chips}</div>
    </div>`;
  }).join('');
}

function renderMap(){
  const c=city();
  const mapName={London:'london_lsoa_station_assignment.png',Birmingham:'birmingham_lsoa_station_assignment.png',Leeds:'leeds_lsoa_station_assignment.png',Sheffield:'sheffield_lsoa_station_assignment.png',Liverpool:'liverpool_lsoa_station_assignment.png'}[currentCity]||'london_lsoa_station_assignment.png';
  document.getElementById('mapTitle').textContent=`${currentCity} LSOA assignment`;
  document.getElementById('mapMeta').textContent=`${c.stations.length} stations`;
  const wrap=document.getElementById('mapWrap');
  wrap.innerHTML=`<img class="map-image" id="stationMapImg" alt="${esc(currentCity)} LSOA assignment map with police stations">`;
  const img=document.getElementById('stationMapImg');
  img.onerror=()=>{wrap.innerHTML='<div class="map-error">Map export not found in the website/maps folder.</div>';};
  img.src=`maps/${mapName}`;
}

function renderChart(){
  // Monthly predicted-crime counts for the selected city (real backend data).
  const monthly=city().monthly||[];
  const data=monthly.length
    ? monthly.map(d=>({label:MONTH_LABELS[d.month]||String(d.month),count:d.count}))
    : city().stations.map(s=>({label:s.postcode,count:s.predicted_severity}));
  const max=Math.max(1,...data.map(d=>Number(d.count)||0));
  document.getElementById('forecastChart').innerHTML=data.map(d=>{
    const height=Math.max(10,(Number(d.count)||0)/max*250);
    return `<div class="bar" data-value="${fmt(d.count)}" style="height:${height}px"><span>${esc(d.label)}</span></div>`;
  }).join('');
}

function renderTopCrimes(){
  const list=city().crime_types||[];
  if(list.length){
    const top=[...list].sort((a,b)=>b.count-a.count).slice(0,6);
    document.getElementById('topCrimes').innerHTML=`<div class="insight-list">${top.map(item=>`
      <div class="insight"><b>${esc(item.crime_type)}</b><p class="muted small">${fmt(item.count)} predicted incidents in 2025.</p></div>
    `).join('')}</div>`;
    return;
  }
  document.getElementById('topCrimes').innerHTML='<div class="note warn">No predicted crime data for this city yet. Run the backend prediction pipeline for this force.</div>';
}

function renderStations(){
  const query=(document.getElementById('searchBox').value||'').toLowerCase().trim();
  const risk=document.getElementById('riskFilter').value;
  const pressureMax=maxPressure();
  const rows=city().stations
    .filter(station=>(risk==='All'||station.risk===risk)&&(`${station.station} ${station.postcode}`.toLowerCase().includes(query)))
    .sort((a,b)=>b.pressure-a.pressure);
  if(!rows.length){
    document.getElementById('stationRows').innerHTML='<tr><td colspan="6" class="empty-state">No stations match the current filter.</td></tr>';
    return;
  }
  document.getElementById('stationRows').innerHTML=rows.map(station=>{
    const meterWidth=clamp(station.pressure/pressureMax*100,6,100);
    const forecast=`${station.forecast_trend_pct>0?'+':''}${station.forecast_trend_pct}%`;
    const focus=focusList(station,3).map(item=>`${esc(item.label)} ${fmt(item.value)}`).join(', ')||'No capacity set';
    return `<tr>
      <td><b>${esc(station.station)}</b></td>
      <td>${esc(station.postcode)}</td>
      <td><span class="badge ${riskClass(station.risk)}">${esc(station.risk)}</span></td>
      <td><div class="pressure"><span>${station.pressure.toFixed(2)}</span><span class="meter"><span style="width:${meterWidth}%;background:${riskColor(station.risk)}"></span></span></div></td>
      <td>${esc(forecast)}</td>
      <td>${focus}</td>
    </tr>`;
  }).join('');
}

function renderFolders(){
  document.getElementById('folderCards').innerHTML=cityList.map(c=>`
    <div class="folder">
      <h3>${esc(c.city)}</h3>
      <div class="path">force: ${esc(c.force)}</div>
      <ul><li>${c.station_count} police stations</li><li>police_stations.csv</li><li>${esc(c.force)}budget_allocation.csv</li><li>lsoa_crime_predictions_${esc(c.force)}.csv</li></ul>
    </div>
  `).join('');
}

function renderFolderDetail(){
  const c=city();
  document.getElementById('selectedFolder').innerHTML=`
    <p class="city-title">backend/data (force: ${esc(c.force)})</p>
    <div class="grid three">
      <div class="insight"><b>police_stations.csv</b><p class="muted small">Station metadata (postcode + coordinates) for this force.</p></div>
      <div class="insight"><b>${esc(c.force)}budget_allocation.csv</b><p class="muted small">Budget % + specialist % per station.</p></div>
      <div class="insight"><b>lsoa_crime_predictions_${esc(c.force)}.csv</b><p class="muted small">Per-LSOA monthly predictions for ${esc(currentCity)}.</p></div>
    </div>
    <h3 style="margin-top:18px">Police bureaus/stations in this folder</h3>
    <div class="station-list">${c.stations.map(station=>`
      <div class="station-card">
        <div><b>${esc(station.station)}</b><br><span>${esc(station.postcode)}</span></div>
        <span class="badge ${riskClass(station.risk)}">${esc(station.risk)}</span>
      </div>
    `).join('')}</div>`;
}

init();

"""

Shows HOW the CPU manages process execution:
  - Process lifecycle: New → Ready → Running → Terminated
  - Live Ready Queue
  - CPU executing step-by-step with animation
  - Context switching (Round Robin)
  - Gantt chart building in real time

Run:  python cpu_scheduler.py
Opens automatically in your default browser. No installs needed.
"""

import webbrowser, tempfile

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CPU Scheduler — Process Execution</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f1117;--surface:#1a1d27;--surface2:#22263a;--border:#2e3350;
  --accent:#6c8aff;--accent2:#a78bfa;--text:#e8eaf6;--muted:#7c82a8;
  --green:#4ade80;--red:#f87171;--amber:#fbbf24;--cyan:#38bdf8;
  --mono:'JetBrains Mono',monospace;--sans:'Inter',sans-serif;
}
body{background:var(--bg);color:var(--text);font-family:var(--sans);min-height:100vh;padding:1.5rem 1rem}
.container{max-width:1100px;margin:0 auto}
header{text-align:center;margin-bottom:2rem}
header h1{font-family:var(--mono);font-size:1.8rem;font-weight:600;letter-spacing:-1px;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.3rem}
header p{color:var(--muted);font-size:.85rem}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.25rem;margin-bottom:.75rem}
.card-title{font-family:var(--mono);font-size:.7rem;font-weight:500;color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:1rem}
.input-row{display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end}
.field{display:flex;flex-direction:column;gap:4px}
label{font-size:11px;color:var(--muted);font-family:var(--mono);text-transform:uppercase;letter-spacing:.5px}
input[type=text],input[type=number]{background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text);font-family:var(--mono);font-size:13px;height:36px;padding:0 10px;outline:none;transition:border-color .15s}
input[type=text]{width:90px}input[type=number]{width:80px}
input:focus{border-color:var(--accent)}
button{height:36px;padding:0 14px;border-radius:8px;border:1px solid var(--border);font-family:var(--mono);font-size:12px;cursor:pointer;transition:all .15s;color:var(--text);background:transparent}
.btn-add{background:var(--accent);color:#fff;border-color:var(--accent)}.btn-add:hover{background:#5a78ee}
.btn-ghost{color:var(--muted)}.btn-ghost:hover{background:var(--surface2);color:var(--text)}
.btn-danger{color:var(--red);border-color:#f8717140}.btn-danger:hover{background:#f8717115}
.btn-run{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border:none;height:44px;width:100%;font-size:14px;font-weight:500;border-radius:10px;margin-top:.75rem}
.btn-run:hover{opacity:.9}
.btn-ctrl{height:36px;padding:0 18px;border-radius:8px;font-size:13px}
.btn-step{background:var(--accent);color:#fff;border-color:var(--accent)}.btn-step:hover{background:#5a78ee}
.btn-play{background:var(--green);color:#0a0a14;border-color:var(--green)}.btn-play:hover{opacity:.85}
.btn-reset{color:var(--amber);border-color:#fbbf2440}.btn-reset:hover{background:#fbbf2415}
.proc-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px;min-height:28px}
.chip{display:flex;align-items:center;gap:5px;padding:3px 8px 3px 10px;border-radius:20px;font-size:11px;font-family:var(--mono)}
.chip-x{cursor:pointer;color:var(--muted);font-size:14px;line-height:1}.chip-x:hover{color:var(--red)}
.empty-msg{color:var(--muted);font-size:12px;font-family:var(--mono)}
.algo-tabs{display:flex;gap:6px;margin-bottom:1rem;flex-wrap:wrap}
.algo-tab{padding:5px 14px;border-radius:20px;font-size:12px;font-family:var(--mono);border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;height:auto}
.algo-tab:hover{border-color:var(--accent);color:var(--text)}
.algo-tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.q-row{display:flex;align-items:center;gap:8px;margin-top:.5rem;font-size:12px;color:var(--muted);font-family:var(--mono)}

/* Execution View */
#exec-view{display:none}
.exec-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.75rem;margin-bottom:.75rem}
@media(max-width:700px){.exec-grid{grid-template-columns:1fr}}
.state-zone{border-radius:10px;padding:1rem;border:1px solid var(--border);min-height:130px}
.zone-title{font-size:10px;font-family:var(--mono);text-transform:uppercase;letter-spacing:1px;margin-bottom:.75rem;display:flex;align-items:center;gap:6px}
.zone-dot{width:8px;height:8px;border-radius:50%}
.pcard{border-radius:8px;padding:8px 10px;margin-bottom:6px;font-family:var(--mono);font-size:12px;border:1px solid transparent;transition:all .3s}
.pcard .pname{font-weight:600;font-size:13px}
.pcard .pinfo{font-size:10px;color:rgba(255,255,255,.55);margin-top:2px}
.cpu-box{background:var(--surface2);border:2px solid var(--accent);border-radius:12px;padding:1rem;text-align:center;min-height:130px;display:flex;flex-direction:column;align-items:center;justify-content:center}
.cpu-label{font-size:9px;font-family:var(--mono);text-transform:uppercase;letter-spacing:2px;color:var(--accent);margin-bottom:.5rem}
.cpu-idle{font-size:13px;color:var(--muted);font-family:var(--mono)}
.cpu-proc{font-size:28px;font-weight:600;font-family:var(--mono)}
.cpu-detail{font-size:11px;color:var(--muted);font-family:var(--mono);margin-top:4px}
.cpu-progress{width:100%;height:6px;background:rgba(108,138,255,.2);border-radius:3px;margin-top:10px;overflow:hidden}
.cpu-progress-fill{height:100%;border-radius:3px;background:var(--accent);transition:width .4s}
.clock{font-family:var(--mono);font-size:13px;font-weight:500;color:var(--cyan);background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:4px 12px;display:inline-flex;align-items:center;gap:6px}
.gantt-scroll{overflow-x:auto;padding-bottom:4px}
.gantt-track{display:flex;align-items:stretch;height:40px}
.gantt-block{display:flex;align-items:center;justify-content:center;font-size:11px;font-family:var(--mono);font-weight:600;border-right:2px solid var(--bg);color:#0a0a14;min-width:18px}
.gantt-ticks{display:flex;margin-top:4px;font-size:10px;font-family:var(--mono);color:var(--muted)}
.log-box{background:var(--surface2);border-radius:8px;padding:.75rem;max-height:150px;overflow-y:auto;font-family:var(--mono);font-size:11px;line-height:1.9}
.log-entry{padding:1px 0;border-bottom:1px solid #ffffff08}
.log-entry:last-child{border:none}
.log-t{color:var(--accent);margin-right:8px}
.log-new{color:#a78bfa}.log-ready{color:var(--cyan)}.log-run{color:var(--green)}.log-done{color:var(--amber)}.log-ctx{color:var(--red)}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-top:.75rem}
.stat-box{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:12px;text-align:center}
.stat-val{font-size:22px;font-weight:600;font-family:var(--mono);color:var(--accent)}
.stat-lbl{font-size:10px;color:var(--muted);margin-top:3px;font-family:var(--mono)}
table{width:100%;border-collapse:collapse;font-size:12px;font-family:var(--mono)}
th{padding:8px 10px;text-align:left;color:var(--muted);font-weight:400;font-size:10px;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--border)}
td{padding:7px 10px;border-bottom:1px solid var(--border);color:var(--text)}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--surface2)}
.pid-badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;color:#0a0a14}
.ctrl-bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.speed-row{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--muted);font-family:var(--mono)}
input[type=range]{width:75px;accent-color:var(--accent)}
.error-msg{background:#f8717120;border:1px solid #f8717140;border-radius:8px;padding:8px 12px;font-size:12px;font-family:var(--mono);color:var(--red);margin-top:6px;display:none}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.legend-item{display:flex;align-items:center;gap:5px;font-size:11px;font-family:var(--mono);color:var(--muted)}
.legend-dot{width:10px;height:10px;border-radius:3px}
.state-legend{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:.75rem;font-size:11px;font-family:var(--mono);color:var(--muted);padding:0 .25rem}
.sl-item{display:flex;align-items:center;gap:5px}
.sl-dot{width:9px;height:9px;border-radius:50%}
</style>
</head>
<body>
<div class="container">

<header>
  <h1>⟨ CPU Scheduler ⟩</h1>
  <p>Watch how the CPU manages process execution — state transitions, ready queue &amp; context switching</p>
</header>

<!-- ── SETUP ── -->
<div id="setup-view">
  <div class="card">
    <div class="card-title">01 — Add Processes</div>
    <div class="input-row">
      <div class="field"><label>Process ID</label><input type="text" id="pid" placeholder="P1" maxlength="6"></div>
      <div class="field"><label>Burst Time</label><input type="number" id="burst" placeholder="5" min="1" max="30"></div>
      <div class="field"><label>Arrival Time</label><input type="number" id="arrival" placeholder="0" min="0" max="30" value="0"></div>
      <button class="btn-add" onclick="addProcess()">+ Add</button>
      <button class="btn-ghost" onclick="loadSample()">Load sample</button>
      <button class="btn-danger" onclick="clearAll()">Clear</button>
    </div>
    <div id="error" class="error-msg"></div>
    <div id="proc-chips" class="proc-chips"><span class="empty-msg">No processes yet</span></div>
  </div>

  <div class="card">
    <div class="card-title">02 — Choose Algorithm</div>
    <div class="algo-tabs">
      <button class="algo-tab active" onclick="setAlgo('FCFS')">FCFS</button>
      <button class="algo-tab" onclick="setAlgo('SJF')">SJF (Non-preemptive)</button>
      <button class="algo-tab" onclick="setAlgo('RR')">Round Robin</button>
    </div>
    <div id="q-row" class="q-row" style="display:none">
      <label>Time Quantum:</label>
      <input type="number" id="quantum" value="2" min="1" max="10" style="width:60px">
    </div>
    <button class="btn-run" onclick="startExecution()">▶  Start Execution Simulation</button>
  </div>
</div>

<!-- ── EXECUTION VIEW ── -->
<div id="exec-view">

  <div class="card" style="padding:.75rem 1.25rem">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
      <div style="display:flex;align-items:center;gap:12px">
        <div class="clock">⏱ Time: <span id="clock-val">0</span></div>
        <div id="algo-badge" style="font-family:var(--mono);font-size:12px;color:var(--accent)"></div>
      </div>
      <div class="ctrl-bar">
        <button class="btn-ctrl btn-step" id="btn-step" onclick="stepOnce()">Step →</button>
        <button class="btn-ctrl btn-play" id="btn-play" onclick="togglePlay()">▶ Auto</button>
        <button class="btn-ctrl btn-reset" onclick="resetSim()">↺ Reset</button>
        <div class="speed-row">Speed <input type="range" id="speed" min="1" max="5" value="3" oninput="document.getElementById('speed-lbl').textContent=this.value+'×'"> <span id="speed-lbl">3×</span></div>
      </div>
    </div>
  </div>

  <div class="state-legend">
    <div class="sl-item"><div class="sl-dot" style="background:#a78bfa"></div>New (not arrived)</div>
    <div class="sl-item"><div class="sl-dot" style="background:#38bdf8"></div>Ready (waiting in queue)</div>
    <div class="sl-item"><div class="sl-dot" style="background:#6c8aff"></div>Running (on CPU)</div>
    <div class="sl-item"><div class="sl-dot" style="background:#fbbf24"></div>Terminated</div>
  </div>

  <div class="exec-grid">

    <div class="state-zone" style="border-color:#38bdf840">
      <div class="zone-title"><div class="zone-dot" style="background:var(--cyan)"></div>Ready Queue</div>
      <div id="zone-ready"><div class="empty-msg">empty</div></div>
    </div>

    <div class="cpu-box">
      <div class="cpu-label">🖥 CPU</div>
      <div id="cpu-content"><div class="cpu-idle">idle</div></div>
      <div class="cpu-progress" style="display:none" id="cpu-prog-wrap">
        <div class="cpu-progress-fill" id="cpu-prog-fill" style="width:0%"></div>
      </div>
      <div id="cpu-detail" class="cpu-detail"></div>
    </div>

    <div class="state-zone" style="border-color:#fbbf2440">
      <div class="zone-title"><div class="zone-dot" style="background:var(--amber)"></div>Terminated</div>
      <div id="zone-done"></div>
    </div>

  </div>

  <div class="card" style="padding:.75rem 1.25rem">
    <div class="card-title" style="margin-bottom:.5rem">Not Yet Arrived (New State)</div>
    <div id="zone-new" class="proc-chips"><span class="empty-msg">—</span></div>
  </div>

  <div class="card">
    <div class="card-title">Gantt Chart — building in real time</div>
    <div class="gantt-scroll">
      <div id="gantt" class="gantt-track"></div>
      <div id="ticks" class="gantt-ticks"></div>
    </div>
    <div id="legend" class="legend"></div>
  </div>

  <div class="card">
    <div class="card-title">Execution Log</div>
    <div id="log" class="log-box"></div>
  </div>

  <div id="final-results" style="display:none">
    <div class="card">
      <div class="card-title">Final Statistics</div>
      <div class="stats-grid" id="stats"></div>
    </div>
    <div class="card">
      <div class="card-title">Process Summary Table</div>
      <table>
        <thead><tr><th>Process</th><th>Burst</th><th>Arrival</th><th>Start</th><th>Finish</th><th>Waiting</th><th>Turnaround</th></tr></thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>
  </div>

</div>
</div>

<script>
const PAL=['#6c8aff','#a78bfa','#34d399','#fb923c','#f472b6','#38bdf8','#facc15','#a3e635','#f87171','#2dd4bf'];
let processes=[],algo='FCFS',simSteps=[],stepIdx=0,playing=false,playTimer=null,procMeta={};
let ganttBlocks=[],donePids=new Set();

function setAlgo(a){
  algo=a;
  document.querySelectorAll('.algo-tab').forEach(b=>b.classList.toggle('active',b.textContent.startsWith(a)));
  document.getElementById('q-row').style.display=a==='RR'?'flex':'none';
}
function showError(msg){const el=document.getElementById('error');el.textContent=msg;el.style.display='block';setTimeout(()=>el.style.display='none',3000)}
function addProcess(){
  const pid=document.getElementById('pid').value.trim()||'P'+(processes.length+1);
  const burst=parseInt(document.getElementById('burst').value);
  const arrival=parseInt(document.getElementById('arrival').value)||0;
  if(!burst||burst<1){showError('Burst time must be ≥ 1');return}
  if(processes.find(p=>p.pid===pid)){showError('ID already exists');return}
  processes.push({pid,burst,arrival,color:PAL[processes.length%PAL.length]});
  document.getElementById('pid').value='';
  document.getElementById('burst').value='';
  document.getElementById('arrival').value='0';
  renderChips();
}
function removeProcess(pid){processes=processes.filter(p=>p.pid!==pid);renderChips()}
function clearAll(){processes=[];renderChips()}
function loadSample(){
  clearAll();
  [['P1',6,0],['P2',4,2],['P3',8,4],['P4',3,6]].forEach(([pid,burst,arrival],i)=>
    processes.push({pid,burst,arrival,color:PAL[i]}));
  renderChips();
}
function renderChips(){
  const el=document.getElementById('proc-chips');
  if(!processes.length){el.innerHTML='<span class="empty-msg">No processes yet</span>';return}
  el.innerHTML=processes.map(p=>`
    <div class="chip" style="border:1px solid ${p.color}40;background:${p.color}18">
      <span style="color:${p.color}">${p.pid}</span>
      <span style="color:#888;font-size:10px">B:${p.burst} A:${p.arrival}</span>
      <span class="chip-x" onclick="removeProcess('${p.pid}')">×</span>
    </div>`).join('');
}
document.getElementById('pid').addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('burst').focus()});
document.getElementById('burst').addEventListener('keydown',e=>{if(e.key==='Enter')addProcess()});

/* ── Build per-tick timeline ─────────────────────────────────────────────── */
function snapRem(jobs){const m={};jobs.forEach(j=>m[j.pid]=j.rem);return {...m}}
function getArrivals(jobs,t){return jobs.filter(j=>j.arrival===t).map(j=>j.pid)}

function buildTimeline(procs,algorithm,quantum){
  const jobs=procs.map(p=>({...p,rem:p.burst,firstStart:null,finish:null}));
  const steps=[];

  if(algorithm==='FCFS'){
    const sorted=[...jobs].sort((a,b)=>a.arrival-b.arrival);
    let t=0;
    for(const p of sorted){
      while(t<p.arrival){
        const ready=jobs.filter(j=>j.rem>0&&j.arrival<=t&&j.pid!==p.pid).map(j=>j.pid);
        steps.push({t,runningPid:null,remMap:snapRem(jobs),readyQueue:[...ready],arrivals:getArrivals(jobs,t),completions:[],contextSwitch:false,rem:null});
        t++;
      }
      if(p.firstStart===null)p.firstStart=t;
      for(let i=0;i<p.burst;i++){
        const ready=jobs.filter(j=>j.rem>0&&j.arrival<=t&&j.pid!==p.pid).map(j=>j.pid);
        const isCtx=steps.length>0&&steps[steps.length-1].runningPid!==p.pid&&i===0;
        steps.push({t,runningPid:p.pid,remMap:snapRem(jobs),readyQueue:ready,arrivals:getArrivals(jobs,t),completions:i===p.burst-1?[p.pid]:[],contextSwitch:isCtx,rem:p.rem-i});
        t++;
      }
      p.rem=0;p.finish=t;
    }
  }

  else if(algorithm==='SJF'){
    const pending=jobs.map(j=>({...j}));
    const jobMap={};pending.forEach(j=>jobMap[j.pid]=j);
    let t=0;
    while(pending.some(j=>j.rem>0)){
      const avail=pending.filter(j=>j.rem>0&&j.arrival<=t);
      if(!avail.length){
        steps.push({t,runningPid:null,remMap:snapRem(pending),readyQueue:[],arrivals:getArrivals(pending,t),completions:[],contextSwitch:false,rem:null});
        t++;continue;
      }
      avail.sort((a,b)=>a.rem-b.rem||a.arrival-b.arrival);
      const p=avail[0];
      if(p.firstStart===null)p.firstStart=t;
      const burstLen=p.rem;
      for(let i=0;i<burstLen;i++){
        const ready=pending.filter(j=>j.rem>0&&j.arrival<=t&&j.pid!==p.pid).map(j=>j.pid);
        const isCtx=steps.length>0&&steps[steps.length-1].runningPid!==p.pid&&i===0;
        steps.push({t,runningPid:p.pid,remMap:snapRem(pending),readyQueue:ready,arrivals:getArrivals(pending,t),completions:i===burstLen-1?[p.pid]:[],contextSwitch:isCtx,rem:p.rem-i});
        t++;
      }
      p.rem=0;p.finish=t;
      // sync back to jobs
      const orig=jobs.find(j=>j.pid===p.pid);
      if(orig){orig.rem=0;orig.finish=t;orig.firstStart=p.firstStart;}
    }
  }

  else{ // RR
    const jbs=jobs.map(j=>({...j}));
    jbs.sort((a,b)=>a.arrival-b.arrival);
    const queue=[];let t=0,cur=null,tq=0;
    const enq=()=>jbs.forEach(j=>{if(j.rem>0&&j.arrival<=t&&j!==cur&&!queue.includes(j))queue.push(j)});
    enq();
    while(jbs.some(j=>j.rem>0)){
      if(!cur){
        if(!queue.length){
          steps.push({t,runningPid:null,remMap:snapRem(jbs),readyQueue:[],arrivals:getArrivals(jbs,t),completions:[],contextSwitch:false,rem:null});
          t++;enq();continue;
        }
        cur=queue.shift();tq=0;
        if(cur.firstStart===null)cur.firstStart=t;
      }
      const ready=queue.map(j=>j.pid);
      const isCtx=steps.length>0&&steps[steps.length-1].runningPid!==cur.pid&&tq===0;
      steps.push({t,runningPid:cur.pid,remMap:snapRem(jbs),readyQueue:ready,arrivals:getArrivals(jbs,t),completions:[],contextSwitch:isCtx,rem:cur.rem});
      cur.rem--;tq++;t++;enq();
      if(cur.rem===0){
        steps[steps.length-1].completions=[cur.pid];
        cur.finish=t;
        const orig=jobs.find(j=>j.pid===cur.pid);
        if(orig){orig.rem=0;orig.finish=t;orig.firstStart=cur.firstStart;}
        cur=null;tq=0;
      }else if(tq>=quantum){queue.push(cur);cur=null;tq=0;}
    }
  }

  return{steps,jobs};
}

/* ── Start simulation ─────────────────────────────────────────────────────── */
function startExecution(){
  if(!processes.length){showError('Add at least one process');return}
  const quantum=parseInt(document.getElementById('quantum').value)||2;
  procMeta={};
  processes.forEach(p=>procMeta[p.pid]={...p});
  const result=buildTimeline(processes,algo,quantum);
  simSteps=result.steps;
  result.jobs.forEach(j=>{
    if(procMeta[j.pid]){procMeta[j.pid].firstStart=j.firstStart;procMeta[j.pid].finish=j.finish;}
  });
  stepIdx=0;playing=false;ganttBlocks=[];donePids=new Set();
  document.getElementById('setup-view').style.display='none';
  document.getElementById('exec-view').style.display='block';
  const labels={FCFS:'First Come First Served',SJF:'Shortest Job First (Non-preemptive)',RR:`Round Robin  —  quantum = ${quantum}`};
  document.getElementById('algo-badge').textContent='▸ '+labels[algo];
  document.getElementById('gantt').innerHTML='';
  document.getElementById('ticks').innerHTML='';
  document.getElementById('log').innerHTML='';
  document.getElementById('final-results').style.display='none';
  document.getElementById('zone-done').innerHTML='';
  document.getElementById('zone-ready').innerHTML='<div class="empty-msg">empty</div>';
  document.getElementById('legend').innerHTML=processes.map(p=>
    `<div class="legend-item"><div class="legend-dot" style="background:${p.color}"></div>${p.pid}</div>`).join('');
  renderStep();
}

function resetSim(){
  clearTimeout(playTimer);playing=false;
  document.getElementById('setup-view').style.display='block';
  document.getElementById('exec-view').style.display='none';
}

/* ── Render one step ──────────────────────────────────────────────────────── */
function renderStep(){
  if(stepIdx>=simSteps.length){showFinal();return}
  const s=simSteps[stepIdx];const t=s.t;
  document.getElementById('clock-val').textContent=t;

  // Log events
  const log=document.getElementById('log');
  if(s.arrivals&&s.arrivals.length)
    s.arrivals.forEach(pid=>{ if(!donePids.has(pid)) addLog(t,`${pid} arrived → enters Ready Queue`,'log-new') });
  if(s.contextSwitch) addLog(t,`⇄ Context switch → CPU dispatches ${s.runningPid}`,'log-ctx');
  else if(s.runningPid&&(stepIdx===0||simSteps[stepIdx-1].runningPid!==s.runningPid))
    addLog(t,`CPU running ${s.runningPid}  (remaining burst: ${s.rem})`,'log-run');
  if(!s.runningPid&&(stepIdx===0||simSteps[stepIdx-1].runningPid!==null))
    addLog(t,'CPU idle — no process in queue','log-ready');
  if(s.completions&&s.completions.length)
    s.completions.forEach(pid=>addLog(t,`✓ ${pid} completed → Terminated`,'log-done'));
  log.scrollTop=log.scrollHeight;

  // New zone
  const newPids=processes.filter(p=>p.arrival>t&&!donePids.has(p.pid));
  document.getElementById('zone-new').innerHTML=newPids.length
    ?newPids.map(p=>`<div class="chip" style="border:1px solid ${p.color}40;background:${p.color}18"><span style="color:${p.color}">${p.pid}</span><span style="color:#888;font-size:10px">arrives t=${p.arrival}</span></div>`).join('')
    :'<span class="empty-msg">—</span>';

  // Ready queue
  document.getElementById('zone-ready').innerHTML=s.readyQueue.length
    ?s.readyQueue.map(pid=>{
        const p=procMeta[pid];
        return `<div class="pcard" style="background:${p.color}20;border-color:${p.color}50">
          <div class="pname" style="color:${p.color}">${pid}</div>
          <div class="pinfo">remaining burst: ${s.remMap[pid]}</div></div>`;
      }).join('')
    :'<div class="empty-msg">empty</div>';

  // CPU
  const cpuContent=document.getElementById('cpu-content');
  const cpuProg=document.getElementById('cpu-prog-wrap');
  const cpuFill=document.getElementById('cpu-prog-fill');
  const cpuDetail=document.getElementById('cpu-detail');
  if(s.runningPid){
    const p=procMeta[s.runningPid];
    const rem=s.rem!==null?s.rem:s.remMap[s.runningPid];
    const pct=Math.round(((p.burst-rem)/p.burst)*100);
    cpuContent.innerHTML=`<div class="cpu-proc" style="color:${p.color}">${s.runningPid}</div>`;
    cpuDetail.textContent=`executed: ${p.burst-rem} / ${p.burst}  (${pct}%)`;
    cpuProg.style.display='block';
    cpuFill.style.width=pct+'%';
    cpuFill.style.background=p.color;
  }else{
    cpuContent.innerHTML='<div class="cpu-idle">idle</div>';
    cpuDetail.textContent='';cpuProg.style.display='none';
  }

  // Terminated
  if(s.completions&&s.completions.length){
    s.completions.forEach(pid=>{
      donePids.add(pid);
      const p=procMeta[pid];
      const wt=p.finish-p.arrival-p.burst;
      const tat=p.finish-p.arrival;
      document.getElementById('zone-done').innerHTML+=
        `<div class="pcard" style="background:#fbbf2420;border-color:#fbbf2460">
          <div class="pname" style="color:${p.color}">${pid}</div>
          <div class="pinfo">WT: ${wt}  TAT: ${tat}</div></div>`;
    });
  }

  // Gantt
  if(s.runningPid){
    const last=ganttBlocks[ganttBlocks.length-1];
    if(last&&last.pid===s.runningPid)last.end=t+1;
    else ganttBlocks.push({pid:s.runningPid,start:t,end:t+1});
  }
  renderGantt(t+1);
  stepIdx++;
}

function renderGantt(total){
  const sc=Math.max(600,total*22)/total;
  document.getElementById('gantt').innerHTML=ganttBlocks.map(g=>{
    const w=Math.max(18,(g.end-g.start)*sc);
    const c=procMeta[g.pid].color;
    return `<div class="gantt-block" style="width:${w}px;background:${c}">${(g.end-g.start)>1?g.pid:''}</div>`;
  }).join('');
  const step=Math.max(1,Math.ceil(total/20));
  let ticks=`<div style="min-width:0;width:0">0</div>`;
  for(let i=step;i<=total;i+=step)ticks+=`<div style="width:${step*sc}px;min-width:${step*sc}px">${i}</div>`;
  document.getElementById('ticks').innerHTML=ticks;
}

function addLog(t,msg,cls){
  document.getElementById('log').innerHTML+=
    `<div class="log-entry"><span class="log-t">t=${String(t).padStart(3,'0')}</span><span class="${cls}">${msg}</span></div>`;
}

/* ── Playback ────────────────────────────────────────────────────────────── */
function stepOnce(){if(!playing)renderStep()}
function togglePlay(){
  playing=!playing;
  document.getElementById('btn-play').textContent=playing?'⏸ Pause':'▶ Auto';
  if(playing)scheduleNext();else clearTimeout(playTimer);
}
function scheduleNext(){
  if(!playing)return;
  const spd=parseInt(document.getElementById('speed').value);
  const delays=[800,500,280,130,50];
  playTimer=setTimeout(()=>{
    renderStep();
    if(stepIdx<simSteps.length)scheduleNext();
    else{playing=false;document.getElementById('btn-play').textContent='▶ Auto';}
  },delays[spd-1]);
}

/* ── Final ───────────────────────────────────────────────────────────────── */
function showFinal(){
  clearTimeout(playTimer);playing=false;
  document.getElementById('btn-play').textContent='▶ Auto';
  document.getElementById('final-results').style.display='block';
  const vals=processes.map(p=>{
    const m=procMeta[p.pid];
    return{pid:p.pid,burst:p.burst,arrival:p.arrival,start:m.firstStart,finish:m.finish,
      waiting:m.finish-p.arrival-p.burst,turnaround:m.finish-p.arrival};
  });
  const avgWT=(vals.reduce((s,v)=>s+v.waiting,0)/vals.length).toFixed(2);
  const avgTAT=(vals.reduce((s,v)=>s+v.turnaround,0)/vals.length).toFixed(2);
  const totalT=Math.max(...vals.map(v=>v.finish));
  const thpt=(vals.length/totalT).toFixed(3);
  document.getElementById('stats').innerHTML=`
    <div class="stat-box"><div class="stat-val">${avgWT}</div><div class="stat-lbl">Avg Waiting Time</div></div>
    <div class="stat-box"><div class="stat-val">${avgTAT}</div><div class="stat-lbl">Avg Turnaround</div></div>
    <div class="stat-box"><div class="stat-val">${thpt}</div><div class="stat-lbl">Throughput</div></div>
    <div class="stat-box"><div class="stat-val">${totalT}</div><div class="stat-lbl">Total Time</div></div>`;
  document.getElementById('table-body').innerHTML=vals.map(r=>{
    const c=procMeta[r.pid].color;
    const wc=r.waiting>parseFloat(avgWT)?'#f87171':'#4ade80';
    return`<tr><td><span class="pid-badge" style="background:${c}">${r.pid}</span></td>
      <td>${r.burst}</td><td>${r.arrival}</td><td>${r.start}</td><td>${r.finish}</td>
      <td style="color:${wc};font-weight:500">${r.waiting}</td><td>${r.turnaround}</td></tr>`;
  }).join('');
  addLog(Math.max(...vals.map(v=>v.finish)),'✓  All processes terminated. Simulation complete.','log-done');
  document.getElementById('final-results').scrollIntoView({behavior:'smooth'});
}
</script>
</body>
</html>"""

tmp = tempfile.NamedTemporaryFile(
    mode="w", suffix=".html", delete=False, encoding="utf-8"
)
tmp.write(HTML)
tmp.close()

path = "file://" + tmp.name.replace("\\", "/")
print("\n" + "=" * 55)
print("  CPU Scheduler — Process Execution Visualizer")
print(f"  Opened: {tmp.name}")
print("=" * 55 + "\n")
webbrowser.open(path)

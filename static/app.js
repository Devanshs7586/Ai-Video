const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
let language = 'english';
let sourceMode = 'url';
let selectedFile = null;
let currentJobId = null;
let currentResult = null;
let pollTimer = null;

const stageOrder = ['queued','audio','transcription','intelligence','knowledge','complete'];

function escapeHtml(value='') {
  return value.replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
}
function renderText(value='') { return escapeHtml(value).replace(/\n/g,'<br>'); }
function fmtBytes(bytes){ if(!bytes) return '0 B'; const units=['B','KB','MB','GB']; let i=Math.floor(Math.log(bytes)/Math.log(1024)); return `${(bytes/Math.pow(1024,i)).toFixed(i?1:0)} ${units[i]}`; }

async function checkHealth(){
  try{
    const r=await fetch('/api/health'); const d=await r.json();
    const el=$('#apiStatus');
    if(d.openai_configured){el.classList.add('ok');el.innerHTML='<i></i> AI stack ready';}
    else{el.classList.add('bad');el.innerHTML='<i></i> OpenAI key missing';}
  }catch{ const el=$('#apiStatus');el.classList.add('bad');el.innerHTML='<i></i> Backend offline'; }
}

$$('.lang').forEach(btn=>btn.addEventListener('click',()=>{
  $$('.lang').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); language=btn.dataset.lang;
  $('#modeNote').innerHTML = language==='english'
    ? '<span class="note-icon">◎</span><div><strong>English mode</strong><p>Speech-to-text runs with local Whisper. OpenAI is used after transcription for analysis and chat.</p></div>'
    : '<span class="note-icon">◎</span><div><strong>Hinglish mode</strong><p>Speech is sent to Sarvam for transcription/translation. OpenAI handles analysis and transcript-grounded chat.</p></div>';
}));

$$('.source-tab').forEach(btn=>btn.addEventListener('click',()=>{
  $$('.source-tab').forEach(b=>b.classList.remove('active'));btn.classList.add('active');sourceMode=btn.dataset.source;
  $('#urlPane').classList.toggle('active',sourceMode==='url');$('#filePane').classList.toggle('active',sourceMode==='file');
}));

$('#clearUrl').onclick=()=>$('#sourceUrl').value='';
const drop=$('#dropzone');
['dragenter','dragover'].forEach(evt=>drop.addEventListener(evt,e=>{e.preventDefault();drop.classList.add('drag')}));
['dragleave','drop'].forEach(evt=>drop.addEventListener(evt,e=>{e.preventDefault();drop.classList.remove('drag')}));
drop.addEventListener('drop',e=>{if(e.dataTransfer.files.length)setFile(e.dataTransfer.files[0])});
$('#fileInput').addEventListener('change',e=>{if(e.target.files.length)setFile(e.target.files[0])});
function setFile(file){ selectedFile=file; $('#fileName').textContent=file.name;$('#fileSize').textContent=fmtBytes(file.size);$('#fileCard').classList.remove('hidden');drop.classList.add('hidden'); }
$('#removeFile').onclick=()=>{selectedFile=null;$('#fileInput').value='';$('#fileCard').classList.add('hidden');drop.classList.remove('hidden')};

function makeWave(){ const w=$('#wave'); w.innerHTML=''; for(let i=0;i<25;i++){const s=document.createElement('span');s.style.animationDelay=`${(i%7)*.07}s`;w.appendChild(s);} }

$('#analyzeBtn').addEventListener('click',startAnalysis);
async function startAnalysis(){
  const error=$('#formError'); error.classList.add('hidden');
  const url=$('#sourceUrl').value.trim();
  if(sourceMode==='url'&&!url){error.textContent='Paste a YouTube URL first.';error.classList.remove('hidden');return;}
  if(sourceMode==='file'&&!selectedFile){error.textContent='Choose an audio or video file first.';error.classList.remove('hidden');return;}
  const fd=new FormData(); fd.append('language',language); if(sourceMode==='url')fd.append('source_url',url);else fd.append('file',selectedFile);
  try{
    const r=await fetch('/api/jobs',{method:'POST',body:fd}); const d=await r.json();
    if(!r.ok)throw new Error(d.detail||'Could not start analysis.');
    currentJobId=d.job_id; showProcessing(); pollJob();
  }catch(e){error.textContent=e.message;error.classList.remove('hidden');}
}

function showProcessing(){
  $('#inputView').classList.add('hidden');$('#resultsView').classList.add('hidden');$('#processingView').classList.remove('hidden');
  $('#jobError').classList.add('hidden'); makeWave(); setRail('audio'); updateProgress({stage:'queued',progress:3,message:'Starting analysis…'});
}
function setRail(stage){
  const idx=stageOrder.indexOf(stage);
  $$('.rail-step').forEach((el,i)=>{el.classList.toggle('active',i===Math.max(0,idx));el.classList.toggle('done',i<idx)});
}
function updateProgress(job){
  $('#progressBar').style.width=`${job.progress||0}%`;$('#progressNumber').textContent=`${job.progress||0}%`;
  $('#stageMessage').textContent=job.message||'Working…';$('#stageBadge').textContent=(job.stage||'processing').toUpperCase();setRail(job.stage);
  const stageIdx=['audio','transcription','intelligence','knowledge'].indexOf(job.stage);
  $$('.pipe-card').forEach((card,i)=>{card.classList.toggle('active',i===stageIdx);card.classList.toggle('done',i<stageIdx||job.stage==='complete');card.querySelector('i').textContent=(i<stageIdx||job.stage==='complete')?'Complete':i===stageIdx?'Running':'Waiting'});
}
async function pollJob(){
  clearTimeout(pollTimer);
  try{
    const r=await fetch(`/api/jobs/${currentJobId}`);const job=await r.json(); if(!r.ok)throw new Error(job.detail||'Status check failed.');
    updateProgress(job);
    if(job.status==='complete'){currentResult=job.result;showResults();return;}
    if(job.status==='error'){throw new Error(job.error||job.message||'Analysis failed.');}
    pollTimer=setTimeout(pollJob,1300);
  }catch(e){$('#jobError').textContent=e.message;$('#jobError').classList.remove('hidden');}
}

function showResults(){
  $('#processingView').classList.add('hidden');$('#inputView').classList.add('hidden');$('#resultsView').classList.remove('hidden');setRail('complete');
  $('#resultTitle').textContent=currentResult.title||'Untitled analysis';$('#resultWords').textContent=`${(currentResult.word_count||0).toLocaleString()} words`;$('#resultLanguage').textContent=currentResult.language==='hinglish'?'Hinglish → English':'English';
  $('#summaryText').innerHTML=renderText(currentResult.summary);$('#actionsText').innerHTML=renderText(currentResult.action_items);$('#decisionsText').innerHTML=renderText(currentResult.decisions);$('#questionsText').innerHTML=renderText(currentResult.questions);$('#transcriptText').textContent=currentResult.transcript;
  $('#actionsPreview').innerHTML=renderText(currentResult.action_items);$('#decisionsPreview').innerHTML=renderText(currentResult.decisions);
  openTab('overview');
}
function openTab(name){
  $$('#resultTabs button').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));$$('.tab-panel').forEach(p=>p.classList.remove('active'));$(`#${name}Panel`).classList.add('active');
}
$$('#resultTabs button').forEach(b=>b.onclick=()=>openTab(b.dataset.tab));$$('[data-open-tab]').forEach(b=>b.onclick=()=>openTab(b.dataset.openTab));

$$('.copy-btn[data-copy]').forEach(btn=>btn.onclick=async()=>{const el=document.getElementById(btn.dataset.copy);await navigator.clipboard.writeText(el.innerText);const old=btn.textContent;btn.textContent='Copied';setTimeout(()=>btn.textContent=old,1000)});
$('#downloadTranscript').onclick=()=>{if(!currentResult)return;const blob=new Blob([currentResult.transcript],{type:'text/plain'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`${(currentResult.title||'transcript').replace(/[^a-z0-9]+/gi,'_')}.txt`;a.click();URL.revokeObjectURL(a.href)};
$('#transcriptSearch').addEventListener('input',e=>{const q=e.target.value.trim();const t=currentResult?.transcript||'';if(!q){$('#transcriptText').textContent=t;return;}const re=new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`,'gi');$('#transcriptText').innerHTML=escapeHtml(t).replace(re,'<mark>$1</mark>')});

$('#chatForm').addEventListener('submit',async e=>{e.preventDefault();const input=$('#chatInput');const q=input.value.trim();if(!q||!currentJobId)return;input.value='';addMessage('user',q);const loader=addMessage('ai','Thinking from the transcript…');
  try{const r=await fetch(`/api/jobs/${currentJobId}/chat`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})});const d=await r.json();if(!r.ok)throw new Error(d.detail||'Chat failed.');loader.querySelector('p').textContent=d.answer;}catch(err){loader.querySelector('p').textContent=`Error: ${err.message}`;}
});
function addMessage(type,text){const div=document.createElement('div');div.className=`message ${type}`;div.innerHTML=`<span>${type==='ai'?'AI':'YOU'}</span><p></p>`;div.querySelector('p').textContent=text;$('#messages').appendChild(div);$('#messages').scrollTop=$('#messages').scrollHeight;return div;}
$$('.suggestions button').forEach(b=>b.onclick=()=>{$('#chatInput').value=b.textContent;$('#chatForm').requestSubmit()});

function resetApp(){clearTimeout(pollTimer);currentJobId=null;currentResult=null;$('#processingView').classList.add('hidden');$('#resultsView').classList.add('hidden');$('#inputView').classList.remove('hidden');setRail('input');$('#progressBar').style.width='0%';}
$('#newAnalysis').onclick=resetApp;$('#resetDuring').onclick=resetApp;

checkHealth();

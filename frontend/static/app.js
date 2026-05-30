// Offline Field Assistant — frontend app
// Vanilla JS, no dependencies, no build step required.

'use strict';

const API = '';  // same origin

// ── Tab navigation ────────────────────────────────────────────────────────────

const TAB_LOADERS = {
  home: loadHome,
  agents: loadAgents,
  projects: loadProjects,
  library: loadLibrary,
  notes: loadNotes,
  audio: () => {},
  network: loadNetwork,
  logs: loadLogs,
  settings: loadSettings,
};

function showTab(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));

  const section = document.getElementById('tab-' + name);
  if (section) section.classList.add('active');

  const tab = [...document.querySelectorAll('.nav-tab')].find(t => t.textContent.toLowerCase().trim() === name.toLowerCase());
  if (tab) tab.classList.add('active');

  const loader = TAB_LOADERS[name];
  if (loader) loader();
}

// ── Utility helpers ───────────────────────────────────────────────────────────

async function apiFetch(path) {
  const r = await fetch(API + path);
  if (!r.ok) throw new Error(`HTTP ${r.status} from ${path}`);
  return r.json();
}

function el(id) { return document.getElementById(id); }

function setHtml(id, html) {
  const e = el(id);
  if (e) e.innerHTML = html;
}

function setText(id, text) {
  const e = el(id);
  if (e) e.textContent = text;
}

function show(id) { const e = el(id); if (e) e.style.display = ''; }
function hide(id) { const e = el(id); if (e) e.style.display = 'none'; }

function dotHtml(ok) {
  const cls = ok ? 'dot-green' : 'dot-red';
  const label = ok ? 'Online' : 'Offline';
  return `<span class="status-dot ${cls}"></span>${label}`;
}

function formatTs(ts) {
  if (!ts) return '—';
  try {
    return new Date(ts).toLocaleTimeString();
  } catch { return ts; }
}

// ── Home ─────────────────────────────────────────────────────────────────────

async function loadHome() {
  hide('home-content');
  hide('home-error');
  show('home-loading');
  try {
    const d = await apiFetch('/api/status');
    hide('home-loading');
    show('home-content');

    setHtml('status-backend', dotHtml(d.backend?.ok));
    setText('status-version', `v${d.backend?.version || '?'}`);

    // Fix 1: LLM backend card — mode-aware (OpenAI vs Ollama)
    const llm = d.llm_backend;
    if (llm && llm.mode === 'openai') {
      setHtml('status-ollama', `<span class="status-dot dot-green"></span>OpenAI`);
      setText('status-model', llm.model || '—');
    } else {
      setHtml('status-ollama', dotHtml(d.ollama?.available));
      setText('status-model', (llm?.model || d.ollama?.default_model || '—'));
    }

    const t = d.backend?.local_time ? new Date(d.backend.local_time).toLocaleString() : '—';
    setText('status-time', t);

    setText('status-url', d.network?.dashboard_url_hint || '—');

    const paths = d.paths || {};
    const pathsHtml = Object.entries(paths)
      .map(([k, v]) => '<div><span style="color:var(--text-muted)">' + escHtml(k) + ':</span> ' + escHtml(v) + '</div>')
      .join('');
    setHtml('status-paths', pathsHtml || '—');

    setText('status-last-event', d.last_event || 'None');

  } catch (err) {
    hide('home-loading');
    show('home-error');
    setText('home-error-msg', String(err));
  }
}

// ── Agents ───────────────────────────────────────────────────────────────────

let agentData = [];

async function loadAgents() {
  if (agentData.length > 0) return; // already loaded
  try {
    const d = await apiFetch('/api/agents');
    agentData = d.agents || [];
    const sel = el('agent-select');
    sel.innerHTML = agentData.map(a =>
      `<option value="${a.agent_id}">${a.name}${a.prompt_available ? '' : ' (prompt missing)'}</option>`
    ).join('');
    onAgentChange();
  } catch (err) {
    el('agent-select').innerHTML = '<option value="">Failed to load agents</option>';
  }
}

function onAgentChange() {
  const sel = el('agent-select');
  const agent = agentData.find(a => a.agent_id === sel.value);
  setText('agent-description', agent ? agent.description : 'Select an agent.');
}

async function sendMessage() {
  const sel = el('agent-select');
  const agentId = sel.value;
  const message = el('agent-message').value.trim();
  const context = el('agent-context').value.trim();

  if (!agentId) { showResponseError('Please select an agent.', null); return; }
  if (!message) { showResponseError('Please enter a message.', null); return; }

  el('send-btn').disabled = true;
  hide('copy-row');
  hide('recovery-hint-box');
  hide('elapsed-time');
  show('agent-loading');

  const ra = el('response-area');
  ra.className = 'empty';
  ra.textContent = '';

  // Fix 5: scroll response area into view so user knows to look there
  ra.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  try {
    const body = { message };
    if (context) body.context = context;

    const r = await fetch(API + `/api/agents/${encodeURIComponent(agentId)}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const d = await r.json();
    hide('agent-loading');
    el('send-btn').disabled = false;

    if (d.ok) {
      ra.className = '';
      ra.textContent = d.response || '(empty response)';
      show('copy-row');
      if (d.elapsed_ms) {
        el('elapsed-time').textContent = `Response in ${(d.elapsed_ms / 1000).toFixed(1)}s  ·  model: ${d.model}  ·  log: ${d.log_id}`;
        show('elapsed-time');
      }
    } else {
      showResponseError(d.error || 'Unknown error.', d.recovery_hint);
      if (d.elapsed_ms) {
        el('elapsed-time').textContent = `Failed after ${(d.elapsed_ms / 1000).toFixed(1)}s`;
        show('elapsed-time');
      }
    }

    // Fix 5: scroll again after content is rendered
    ra.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  } catch (err) {
    hide('agent-loading');
    el('send-btn').disabled = false;
    showResponseError(`Request failed: ${err}. Is the backend running?`, 'Reload the page and check that the backend is still running.');
  }
}

function showResponseError(msg, hint) {
  const ra = el('response-area');
  ra.className = 'error-state';
  ra.textContent = '⚠ ' + msg;
  if (hint) {
    el('recovery-hint-box').textContent = '→ ' + hint;
    show('recovery-hint-box');
  }
}

function clearAgentPanel() {
  el('agent-message').value = '';
  el('agent-context').value = '';
  const ra = el('response-area');
  ra.className = 'empty';
  ra.textContent = 'Response will appear here.';
  hide('copy-row');
  hide('recovery-hint-box');
  hide('elapsed-time');
}

function copyResponse() {
  const text = el('response-area').textContent;
  if (!text || text === 'Response will appear here.') return;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(showCopyConfirm);
  } else {
    // Fallback for non-secure contexts (plain HTTP on Android LAN)
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
      document.execCommand('copy');
      showCopyConfirm();
    } catch (err) {
      alert('Auto-copy not supported here. Please long-press and copy the text manually.');
    }
    document.body.removeChild(ta);
  }
}

function showCopyConfirm() {
  const c = el('copy-confirm');
  c.classList.add('show');
  setTimeout(() => c.classList.remove('show'), 2000);
}

// ── Projects ─────────────────────────────────────────────────────────────────

// Fix 2: always re-fetches on tab switch, shows clear error on failure
async function loadProjects() {
  const dirEl = el('projects-workspace-dir');
  const errEl = el('projects-dir-error');
  dirEl.textContent = 'Loading...';
  if (errEl) errEl.style.display = 'none';
  try {
    const d = await apiFetch('/api/projects');
    dirEl.textContent = d.workspace_dir || '—';
  } catch (err) {
    dirEl.textContent = '—';
    if (errEl) {
      errEl.textContent = 'Could not load path: ' + err;
      errEl.style.display = '';
    }
  }
}

// ── Library ──────────────────────────────────────────────────────────────────

async function loadLibrary() {
  const badge = el('library-badge');
  try {
    const d = await apiFetch('/api/library');
    const items = d.items || [];
    const hasItems = items.length > 0;

    badge.textContent = hasItems ? 'Live' : 'Empty';
    badge.className = 'badge ' + (hasItems ? 'live' : 'scaffold');

    if (!hasItems) {
      show('library-empty-hint');
      hide('library-summary');
      hide('library-how-to');
      hide('library-items-list');
      return;
    }

    hide('library-empty-hint');
    show('library-summary');
    show('library-how-to');
    show('library-items-list');

    setText('library-item-count', `${items.length} pages indexed`);
    setText('library-exports-dir', d.notion_exports_dir || '—');

    // Group by section
    const sections = {};
    for (const item of items) {
      const sec = item.section || 'Other';
      if (!sections[sec]) sections[sec] = [];
      sections[sec].push(item);
    }

    const html = Object.entries(sections).map(([sec, pages]) => `
      <div class="library-section-header">${escHtml(sec)}</div>
      ${pages.map(p => `
        <div class="library-item">
          <div class="library-item-title">${escHtml(p.title)}</div>
          ${p.tags.length ? `<div class="library-item-tags">${p.tags.map(t => `<span class="lib-tag">${escHtml(t)}</span>`).join('')}</div>` : ''}
          ${p.local_agent_use ? `<div class="library-item-use">${escHtml(p.local_agent_use)}</div>` : ''}
        </div>
      `).join('')}
    `).join('');

    el('library-items-list').innerHTML = html;

  } catch (err) {
    badge.textContent = 'Error';
    badge.className = 'badge scaffold';
    el('library-items-list').innerHTML = `<div class="info-box warning"><p>Could not load library: ${escHtml(String(err))}</p></div>`;
  }
}

// ── Notes ────────────────────────────────────────────────────────────────────

async function loadNotes() {
  try {
    const d = await apiFetch('/api/notes');
    const pathKeys = ['inbox', 'processed', 'ready_for_notion', 'archived'];
    const html = pathKeys
      .filter(k => d[k])
      .map(k => '<div><span style="color:var(--text-muted)">' + escHtml(k) + ':</span> ' + escHtml(d[k]) + '</div>')
      .join('');
    el('notes-paths').innerHTML = html || escHtml(d.notes_dir) || '—';
  } catch (err) {
    el('notes-paths').textContent = 'Could not load: ' + err;
  }
}

// ── Network ──────────────────────────────────────────────────────────────────

// Fix 3: show localhost for local access; show real LAN IP for Android URL
async function loadNetwork() {
  try {
    const d = await apiFetch('/api/network/status');
    const localHost = (d.host === '0.0.0.0' || !d.host) ? 'localhost' : d.host;
    el('network-host').textContent = `${localHost}:${d.port || 8080}`;

    const urlEl = el('network-url');
    const subEl = el('network-url-sub');
    const hint = d.dashboard_url_hint || '—';
    urlEl.textContent = hint;

    // If LAN IP was detected, remove the placeholder hint
    if (subEl) {
      if (d.lan_ip && !d.lan_ip.startsWith('<')) {
        subEl.textContent = 'Auto-detected LAN address — use this on your Android phone';
      } else {
        subEl.textContent = 'Run: ipconfig | findstr IPv4 — then replace <mini-pc-ip>';
      }
    }
  } catch (err) {
    el('network-host').textContent = 'Could not load.';
    el('network-url').textContent = '—';
  }
}

// ── Logs ─────────────────────────────────────────────────────────────────────

async function loadLogs() {
  hide('logs-empty');
  show('logs-loading');
  el('logs-list').innerHTML = '';
  try {
    const d = await apiFetch('/api/logs/recent');
    hide('logs-loading');
    const logs = d.logs || [];
    if (logs.length === 0) {
      show('logs-empty');
      return;
    }
    el('logs-list').innerHTML = logs.map(renderLogEntry).join('');
  } catch (err) {
    hide('logs-loading');
    el('logs-list').innerHTML = `<div class="info-box warning"><p>Could not load logs: ${err}</p></div>`;
  }
}

function renderLogEntry(entry) {
  const ts = formatTs(entry.timestamp);

  // Agent call entry
  if (entry.agent_id) {
    const msg = entry.ok
      ? `${entry.agent_id} → ${entry.model} (${entry.elapsed_ms}ms)`
      : `${entry.agent_id} failed: ${entry.error || '?'}`;
    return `<div class="log-entry">
      <div class="log-ts">${ts} · agent call · id:${entry.id || '?'}</div>
      <div><span class="log-type log-type-${entry.ok ? 'ok' : 'fail'}">${entry.ok ? 'ok' : 'fail'}</span>
      <span class="log-msg">${escHtml(msg)}</span></div>
      ${entry.message_preview ? `<div style="font-size:12px;color:var(--text-muted);margin-top:4px">"${escHtml(entry.message_preview.substring(0, 80))}..."</div>` : ''}
    </div>`;
  }

  // Backend event entry
  const stClass = entry.status === 'ok' ? 'ok' : entry.status === 'warn' ? 'warn' : 'fail';
  return `<div class="log-entry">
    <div class="log-ts">${ts} · ${escHtml(entry.event_type || 'event')}</div>
    <div><span class="log-type log-type-${stClass}">${escHtml(entry.status || '?')}</span>
    <span class="log-msg">${escHtml(entry.details || '')}</span></div>
    ${entry.error ? `<div class="log-err">${escHtml(entry.error)}</div>` : ''}
  </div>`;
}

function escHtml(s) {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Settings ─────────────────────────────────────────────────────────────────

async function loadSettings() {
  try {
    const d = await apiFetch('/api/settings');
    const cfg = d.config || {};
    const rows = Object.entries(cfg)
      .map(([k, v]) => `<tr><td>${escHtml(k)}</td><td>${escHtml(String(v))}</td></tr>`)
      .join('');
    el('settings-table').innerHTML = rows || '<tr><td colspan="2">No config data.</td></tr>';
  } catch (err) {
    el('settings-table').innerHTML = `<tr><td colspan="2">Could not load settings: ${escHtml(String(err))}</td></tr>`;
  }
}

// ── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  loadHome();
});

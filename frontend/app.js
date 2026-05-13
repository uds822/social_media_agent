/**
 * app.js — Buniyaad Admin Dashboard
 * Handles auth, post loading, approval, editing, history, and settings.
 */

// ── Configuration ────────────────────────────────────────────────────────────
// Auto-detect backend from same host as frontend (works on phone, laptop, any device)
const DEFAULT_API = "https://social-media-agent-47b8.onrender.com";
function getApiBase() {
  return localStorage.getItem('buniyaad_api_url') || DEFAULT_API;
}

function getToken() {
  return localStorage.getItem('buniyaad_token');
}

function setToken(t) {
  localStorage.setItem('buniyaad_token', t);
}

function clearToken() {
  localStorage.removeItem('buniyaad_token');
}

// ── API helpers ───────────────────────────────────────────────────────────────
async function api(path, method = 'GET', body = null) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${getApiBase()}${path}`, opts);
  if (res.status === 401) { logout(); throw new Error('Unauthorized'); }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────
async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const btnText = document.getElementById('login-btn-text');
  const spinner = document.getElementById('login-spinner');
  const errMsg = document.getElementById('login-error');

  btnText.textContent = 'Signing in…';
  spinner.classList.remove('hidden');
  btn.disabled = true;
  errMsg.classList.add('hidden');

  try {
    const data = await api('/auth/login', 'POST', {
      username: document.getElementById('login-username').value,
      password: document.getElementById('login-password').value,
    });
    setToken(data.token);
    showApp();
  } catch (err) {
    errMsg.textContent = err.message || 'Login failed. Check your credentials.';
    errMsg.classList.remove('hidden');
  } finally {
    btnText.textContent = 'Sign In';
    spinner.classList.add('hidden');
    btn.disabled = false;
  }
}

function togglePassword() {
  const input = document.getElementById('login-password');
  const btn = document.getElementById('show-pass-btn');
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = '🙈 HIDE PASSWORD';
  } else {
    input.type = 'password';
    btn.textContent = '👁 SHOW PASSWORD';
  }
}

function showLoginScreen(e) {
  if (e) e.preventDefault();
  document.getElementById('screen-reset').classList.add('hidden');
  document.getElementById('screen-reset').classList.remove('active');
  document.getElementById('screen-register').classList.add('hidden');
  document.getElementById('screen-register').classList.remove('active');
  document.getElementById('screen-login').classList.add('active');
  document.getElementById('screen-login').classList.remove('hidden');
}

function showResetScreen(e) {
  if (e) e.preventDefault();
  document.getElementById('screen-login').classList.add('hidden');
  document.getElementById('screen-login').classList.remove('active');
  document.getElementById('screen-register').classList.add('hidden');
  document.getElementById('screen-register').classList.remove('active');
  document.getElementById('screen-reset').classList.add('active');
  document.getElementById('screen-reset').classList.remove('hidden');
}

function showRegisterScreen(e) {
  if (e) e.preventDefault();
  document.getElementById('screen-login').classList.add('hidden');
  document.getElementById('screen-login').classList.remove('active');
  document.getElementById('screen-reset').classList.add('hidden');
  document.getElementById('screen-reset').classList.remove('active');
  document.getElementById('screen-register').classList.add('active');
  document.getElementById('screen-register').classList.remove('hidden');
}

async function handleRegister(e) {
  e.preventDefault();
  const btn = document.getElementById('register-btn');
  const btnText = document.getElementById('register-btn-text');
  const errMsg = document.getElementById('register-error');
  
  btnText.textContent = 'Creating...';
  btn.disabled = true;
  errMsg.classList.add('hidden');
  
  try {
    const data = await api('/auth/register', 'POST', {
      username: document.getElementById('register-username').value,
      password: document.getElementById('register-password').value,
    });
    alert(data.message);
    document.getElementById('register-form').reset();
    showLoginScreen();
  } catch (err) {
    errMsg.textContent = err.message || 'Failed to create account.';
    errMsg.classList.remove('hidden');
  } finally {
    btnText.textContent = 'Create Account';
    btn.disabled = false;
  }
}

async function handleResetPassword(e) {
  e.preventDefault();
  const btn = document.getElementById('reset-btn');
  const btnText = document.getElementById('reset-btn-text');
  const errMsg = document.getElementById('reset-error');
  
  btnText.textContent = 'Resetting...';
  btn.disabled = true;
  errMsg.classList.add('hidden');
  
  try {
    const data = await api('/auth/reset-password', 'POST', {
      username: document.getElementById('reset-username').value,
      backup_code: document.getElementById('reset-code').value,
      new_password: document.getElementById('reset-password').value,
    });
    alert(data.message);
    document.getElementById('reset-form').reset();
    showLoginScreen();
  } catch (err) {
    errMsg.textContent = err.message || 'Failed to reset password.';
    errMsg.classList.remove('hidden');
  } finally {
    btnText.textContent = 'Reset Password';
    btn.disabled = false;
  }
}

function logout() {
  clearToken();
  document.getElementById('screen-app').classList.add('hidden');
  document.getElementById('screen-app').classList.remove('active');
  document.getElementById('screen-reset').classList.add('hidden');
  document.getElementById('screen-reset').classList.remove('active');
  document.getElementById('screen-login').classList.add('active');
  document.getElementById('screen-login').classList.remove('hidden');
  currentPost = null;
}

// ── App initialisation ────────────────────────────────────────────────────────
function showApp() {
  document.getElementById('screen-login').classList.remove('active');
  document.getElementById('screen-login').classList.add('hidden');
  document.getElementById('screen-app').classList.remove('hidden');
  document.getElementById('screen-app').classList.add('active');
  document.getElementById('server-url-display').textContent = getApiBase();
  document.getElementById('server-url-input').value = getApiBase();
  showTab('tab-today');
  loadPendingPost();
}

// Check if already logged in on page load
window.addEventListener('DOMContentLoaded', () => {
  if (getToken()) {
    showApp();
  }
});

// ── Tabs ──────────────────────────────────────────────────────────────────────
function showTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(t => {
    t.classList.remove('active');
    t.classList.add('hidden');
  });
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  const tab = document.getElementById(tabId);
  tab.classList.remove('hidden');
  tab.classList.add('active');

  const navMap = { 'tab-today': 'nav-today', 'tab-history': 'nav-history', 'tab-settings': 'nav-settings' };
  if (navMap[tabId]) document.getElementById(navMap[tabId]).classList.add('active');

  if (tabId === 'tab-history') loadHistory();
  if (tabId === 'tab-settings') loadStatus();
}

// ── State ─────────────────────────────────────────────────────────────────────
let currentPost = null;
let editingCaption = false;
let editingHashtags = false;

// ── Today's post ──────────────────────────────────────────────────────────────
async function loadPendingPost() {
  setPostState('loading');
  try {
    const data = await api('/api/posts/pending');
    if (data.post) {
      currentPost = data.post;
      renderPost(data.post);
      setPostState('post');
    } else {
      setPostState('empty');
    }
  } catch (err) {
    setPostState('empty');
    showStatusMsg(`Error: ${err.message}`, 'error');
  }
}

function setPostState(state) {
  const loading = document.getElementById('post-loading');
  const empty = document.getElementById('post-empty');
  const card = document.getElementById('post-card');

  // Force hide all three (add hidden class)
  loading.classList.add('hidden');
  empty.classList.add('hidden');
  card.classList.add('hidden');

  // Show the right one by removing hidden class
  if (state === 'loading') {
    loading.classList.remove('hidden');
  } else if (state === 'empty') {
    empty.classList.remove('hidden');
  } else if (state === 'post') {
    card.classList.remove('hidden');
  }
}

function renderPost(post) {
  // Image — rebuild the wrapper so onerror can't break it permanently
  const imgWrapper = document.querySelector('.post-image-wrapper');
  if (imgWrapper) {
    if (post.image_url) {
      imgWrapper.innerHTML = `<img id="post-image" src="${post.image_url}" alt="Generated post image"
        style="width:100%;border-radius:12px;"
        onerror="this.parentElement.innerHTML='<div class=\\'no-image\\'>🖼️<br/>Image not available</div>'" />`;
    } else {
      imgWrapper.innerHTML = '<div class="no-image">🖼️<br/>Image generating…</div>';
    }
  }

  // Badges
  document.getElementById('post-type-badge').textContent = formatPostType(post.post_type);
  document.getElementById('post-subject-badge').textContent = post.subject || '';
  document.getElementById('post-class-badge').textContent = post.class_level || '';

  // Fact check
  const fc = document.getElementById('fact-check-indicator');
  const fcMap = {
    verified: '<span class="badge" style="background:linear-gradient(135deg,#1B5E20,#2E7D32)">✅ Fact Verified</span>',
    unverified: '<span class="badge" style="background:linear-gradient(135deg,#E65100,#F57C00)">⚠️ Fact Unverified</span>',
    failed: '<span class="badge" style="background:linear-gradient(135deg,#7F0000,#B71C1C)">❌ Fact Check Failed</span>',
  };
  fc.innerHTML = fcMap[post.fact_check_status] || '';

  // Caption & hashtags
  document.getElementById('caption-display').textContent = post.caption || '';
  document.getElementById('hashtags-display').textContent = post.hashtags || '';
  document.getElementById('caption-edit').value = post.caption || '';
  document.getElementById('hashtags-edit').value = post.hashtags || '';

  document.getElementById('post-suggestions').textContent = post.suggestions || 'No suggestions available.';

  // Status msg
  document.getElementById('status-msg').classList.add('hidden');
  editingCaption = false;
  editingHashtags = false;
  document.getElementById('caption-edit').classList.add('hidden');
  document.getElementById('hashtags-edit').classList.add('hidden');
  document.getElementById('caption-display').classList.remove('hidden');
  document.getElementById('hashtags-display').classList.remove('hidden');
  document.getElementById('save-edits-bar').classList.add('hidden');
}

function formatPostType(t) {
  const m = {
    question_of_day: 'Q of the Day',
    word_of_day: 'Word of Day',
    interesting_fact: 'Interesting Fact',
    festival_greeting: 'Festival',
    trending_awareness: 'Trending/Exam',
    quiz_poll: 'Quiz / Poll',
    motivational_quote: 'Motivation'
  };
  return m[t] || t;
}

// ── Language ──────────────────────────────────────────────────────────────────
let selectedLanguage = 'english';

function setLanguage(lang) {
  selectedLanguage = lang;
  // Toggle button styles
  document.getElementById('lang-en').classList.toggle('lang-btn-active', lang === 'english');
  document.getElementById('lang-hi').classList.toggle('lang-btn-active', lang === 'hindi');
  // Toggle info notes
  document.getElementById('lang-note-en').classList.toggle('hidden', lang !== 'english');
  document.getElementById('lang-note-hi').classList.toggle('hidden', lang !== 'hindi');
}

// ── Generate ──────────────────────────────────────────────────────────────────
async function generatePost(postType, subject, classLevel) {
  const icon = document.getElementById('gen-btn-icon');
  icon.textContent = '⏳';
  setPostState('loading');
  showStatusMsg('AI is generating your post… this takes ~15 seconds.', 'info');

  // Record when generate was clicked — only accept posts created AFTER this moment
  const generateClickedAt = new Date().toISOString();
  const previousPostId = currentPost ? currentPost.id : null;

  try {
    // Word of Day and Admission always use English regardless of language setting
    const langToSend = (postType === 'word_of_day' || postType === 'admission_post')
      ? 'english'
      : selectedLanguage;

    await api('/api/posts/generate', 'POST', {
      post_type: postType || null,
      subject: subject || null,
      class_level: classLevel || null,
      language: langToSend,
    });
    // Poll every 3s up to 20 times (~65s total)
    let attempts = 0;
    const poll = async () => {
      attempts++;
      if (attempts === 10) {
        showStatusMsg('Still generating… AI is thinking hard, please wait ⏳', 'info');
      }
      try {
        const data = await api('/api/posts/pending');
        if (data && data.post && data.post.id !== previousPostId) {
          currentPost = data.post;
          renderPost(data.post);
          setPostState('post');
          showStatusMsg('Post generated successfully!', 'success');
          icon.textContent = '✨';
          return;
        }
      } catch (_) { }
      if (attempts < 20) {
        setTimeout(poll, 3000);
      } else {
        setPostState('empty');
        showStatusMsg('Generation timed out. Check History tab or tap Refresh.', 'error');
        icon.textContent = '✨';
      }
    };
    setTimeout(poll, 2000); // first check after 2s
  } catch (err) {
    setPostState('empty');
    showStatusMsg('Generation failed: ' + err.message, 'error');
    icon.textContent = '✨';
  }
}

// ── Download & Copy (Manual Posting) ──────────────────────────────────────────
async function downloadPost() {
  if (!currentPost || !currentPost.image_url) return;

  const btn = document.querySelector('button[onclick="downloadPost()"]');
  const originalText = btn ? btn.innerHTML : '';
  if (btn) btn.innerHTML = '⏳ Processing...';

  // 1. Copy caption and hashtags to clipboard
  const caption = document.getElementById('caption-display').textContent || '';
  const hashtags = document.getElementById('hashtags-display').textContent || '';
  const fullText = `${caption}\n\n${hashtags}`.trim();

  try {
    await navigator.clipboard.writeText(fullText);
    showStatusMsg('📋 Caption copied! Preparing image...', 'info');
  } catch (err) {
    console.error('Clipboard copy failed:', err);
  }

  // 2. Download the image
  try {
    // Fetch blob
    const response = await fetch(currentPost.image_url, { mode: 'cors' });
    if (!response.ok) throw new Error('Network response was not ok');
    const blob = await response.blob();
    const filename = `buniyaad-${currentPost.post_type}-${Date.now()}.jpg`;

    // Try Native Share API first (Works perfectly in Android App WebViews)
    if (navigator.canShare && navigator.share) {
      const file = new File([blob], filename, { type: blob.type || 'image/jpeg' });
      if (navigator.canShare({ files: [file] })) {
        try {
          await navigator.share({
            title: 'Buniyaad Post',
            text: fullText,
            files: [file]
          });
          showStatusMsg('✅ Image & Caption shared successfully!', 'success');
          if (btn) btn.innerHTML = originalText;
          return;
        } catch (shareErr) {
          console.error('Share rejected/failed:', shareErr);
          // If user just cancelled the share sheet, abort without error
          if (shareErr.name === 'AbortError') {
             if (btn) btn.innerHTML = originalText;
             return;
          }
        }
      }
    }

    // Fallback: standard web download
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl);
      document.body.removeChild(a);
    }, 100);

    setTimeout(() => {
      showStatusMsg('✅ Image downloaded & Caption copied! Ready to post manually.', 'success');
    }, 1500);

  } catch (err) {
    console.error('Download failed:', err);
    // Fallback: just open image in new tab if CORS blocks the download
    window.open(currentPost.image_url, '_blank');
    showStatusMsg('✅ Caption copied! Long-press the opened image to save it.', 'success');
  } finally {
    if (btn) btn.innerHTML = originalText;
  }
}

// ── Approve ───────────────────────────────────────────────────────────────────
async function approvePost() {
  if (!currentPost) return;
  const btn = document.getElementById('approve-btn');
  btn.textContent = '⏳ Publishing…';
  btn.disabled = true;

  try {
    await api(`/api/posts/${currentPost.id}/approve`, 'POST');
    showStatusMsg('🎉 Post approved and being published to Instagram & Facebook!', 'success');
    setTimeout(loadPendingPost, 5000);
  } catch (err) {
    showStatusMsg(`Publish failed: ${err.message}`, 'error');
  } finally {
    btn.textContent = '✅ Approve & Publish';
    btn.disabled = false;
  }
}

// ── Reject ────────────────────────────────────────────────────────────────────
async function rejectPost() {
  if (!currentPost) return;
  if (!confirm('Reject this post?')) return;
  try {
    await api(`/api/posts/${currentPost.id}/reject`, 'POST');
    showStatusMsg('Post rejected.', 'info');
    currentPost = null;
    setTimeout(() => setPostState('empty'), 1500);
  } catch (err) {
    showStatusMsg(`Reject failed: ${err.message}`, 'error');
  }
}

// ── Regenerate ────────────────────────────────────────────────────────────────
async function regeneratePost() {
  if (!currentPost) return;
  if (!confirm('Regenerate this post? The current version will be discarded.')) return;
  setPostState('loading');
  try {
    await api(`/api/posts/${currentPost.id}/regenerate`, 'POST');
    showStatusMsg('🔄 Regenerating… Check back in ~15 seconds.', 'info');
    setTimeout(loadPendingPost, 15000);
  } catch (err) {
    setPostState('post');
    showStatusMsg(`Regenerate failed: ${err.message}`, 'error');
  }
}

// ── Edit caption/hashtags ─────────────────────────────────────────────────────
function toggleEditCaption() {
  editingCaption = !editingCaption;
  document.getElementById('caption-display').classList.toggle('hidden', editingCaption);
  document.getElementById('caption-edit').classList.toggle('hidden', !editingCaption);
  document.getElementById('save-edits-bar').classList.toggle('hidden', !editingCaption && !editingHashtags);
}

function toggleEditHashtags() {
  editingHashtags = !editingHashtags;
  document.getElementById('hashtags-display').classList.toggle('hidden', editingHashtags);
  document.getElementById('hashtags-edit').classList.toggle('hidden', !editingHashtags);
  document.getElementById('save-edits-bar').classList.toggle('hidden', !editingCaption && !editingHashtags);
}

function cancelEdits() {
  editingCaption = false;
  editingHashtags = false;
  document.getElementById('caption-edit').classList.add('hidden');
  document.getElementById('hashtags-edit').classList.add('hidden');
  document.getElementById('caption-display').classList.remove('hidden');
  document.getElementById('hashtags-display').classList.remove('hidden');
  document.getElementById('save-edits-bar').classList.add('hidden');
}

async function saveEdits() {
  if (!currentPost) return;
  const body = {};
  if (editingCaption) body.caption = document.getElementById('caption-edit').value;
  if (editingHashtags) body.hashtags = document.getElementById('hashtags-edit').value;

  try {
    const data = await api(`/api/posts/${currentPost.id}/caption`, 'PATCH', body);
    currentPost = data.post;
    renderPost(data.post);
    showStatusMsg('✅ Caption saved!', 'success');
  } catch (err) {
    showStatusMsg(`Save failed: ${err.message}`, 'error');
  }
}

// ── History ───────────────────────────────────────────────────────────────────
async function loadHistory() {
  document.getElementById('history-loading').classList.remove('hidden');
  document.getElementById('history-list').innerHTML = '';
  document.getElementById('history-empty').classList.add('hidden');

  try {
    const data = await api('/api/posts/history');
    document.getElementById('history-loading').classList.add('hidden');
    if (!data.posts || data.posts.length === 0) {
      document.getElementById('history-empty').classList.remove('hidden');
      return;
    }
    const grid = document.getElementById('history-list');
    data.posts.forEach(p => grid.appendChild(buildHistoryCard(p)));
  } catch (err) {
    document.getElementById('history-loading').classList.add('hidden');
    document.getElementById('history-list').innerHTML =
      `<p style="color:#EF9A9A; padding:16px;">Error: ${err.message}</p>`;
  }
}

function buildHistoryCard(post) {
  const card = document.createElement('div');
  card.className = 'history-card';

  const date = post.published_at || post.created_at;
  const dateStr = date ? new Date(date).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  }) : '';

  const igIcon = post.instagram_post_id ? '📸 Instagram' : '';
  const fbIcon = post.facebook_post_id ? '📘 Facebook' : '';

  card.innerHTML = `
    ${post.image_url
      ? `<img src="${post.image_url}" alt="${formatPostType(post.post_type)}" loading="lazy" />`
      : `<div style="width:100%;aspect-ratio:1;background:var(--surface);display:flex;align-items:center;justify-content:center;font-size:48px;">🖼️</div>`
    }
    <div class="history-card-body">
      <div class="history-card-meta">
        <span class="status-pill status-${post.status}">${post.status}</span>
        <span class="history-date">${dateStr}</span>
      </div>
      <div style="margin-bottom:6px;">
        <span class="badge" style="font-size:11px;">${formatPostType(post.post_type)}</span>
      </div>
      <p class="history-caption">${post.caption || ''}</p>
      <div class="history-platforms">${igIcon} ${fbIcon}</div>
    </div>`;
  return card;
}

// ── Status ────────────────────────────────────────────────────────────────────
async function loadStatus() {
  const list = document.getElementById('api-status-list');
  list.innerHTML = '<div class="center-msg"><div class="big-spinner"></div></div>';

  try {
    const s = await api('/api/status');
    const items = [
      ['OpenRouter API', s.openrouter_configured],
      ['Groq API', s.groq_configured],
      ['NVIDIA API', s.nvidia_configured],
      ['Hugging Face', s.huggingface_configured],
      ['Supabase DB', s.supabase_configured],
      ['Cloudinary', s.cloudinary_configured],
      ['Meta (FB+IG)', s.meta_configured],
      ['Scheduler', s.scheduler_running],
    ];
    list.innerHTML = items.map(([label, ok]) => `
      <div class="status-item">
        <span><span class="status-dot ${ok ? 'dot-ok' : 'dot-err'}"></span>${label}</span>
        <span style="font-size:12px;font-weight:600;color:${ok ? '#34d399' : '#fca5a5'}">${ok ? 'Connected' : 'Not Configured'}</span>
      </div>`).join('');

    // Pre-populate model name inputs with current active models
    const modelMap = {
      'openrouter-model-input': s.openrouter_model,
      'groq-model-input': s.groq_model,
      'nvidia-model-input': s.nvidia_model,
      'huggingface-model-input': s.huggingface_model,
    };
    for (const [id, val] of Object.entries(modelMap)) {
      const el = document.getElementById(id);
      if (el && val) el.value = val;
    }

    // Highlight whichever provider is currently active
    if (s.active_provider) highlightActiveProvider(s.active_provider);

    // Update Top Badges
    const badgeGen = document.getElementById('ui-badge-generator');
    const badgeChk = document.getElementById('ui-badge-checker');
    if (badgeGen && s.active_generator_text) {
      badgeGen.textContent = s.active_generator_text;
      badgeGen.style.color = s.active_generator_color;
    }
    if (badgeChk && s.active_fact_checker) {
      badgeChk.textContent = s.active_fact_checker;
    }
  } catch (err) {
    list.innerHTML = `<p style="color:#EF9A9A;font-size:13px;">Could not reach backend: ${err.message}</p>`;
  }
}

function highlightActiveProvider(provider) {
  const ids = ['nvidia', 'groq', 'openrouter', 'huggingface'];
  ids.forEach(p => {
    const btn = document.getElementById(`prov-btn-${p}`);
    if (btn) btn.classList.toggle('provider-active', p === provider.toLowerCase());
  });
}

async function setActiveProvider(provider) {
  // Optimistic UI update
  highlightActiveProvider(provider);
  const msgEl = document.getElementById('provider-save-msg');
  if (msgEl) { msgEl.style.display = 'none'; }

  try {
    await api('/api/settings/keys', 'POST', { active_provider: provider });
    // Update badge immediately with provider name + current model from input
    _refreshGeneratorBadge(provider);
    if (msgEl) {
      msgEl.style.color = '#34d399';
      msgEl.textContent = `✅ Switched to ${provider.toUpperCase()}! It will be used for next generation.`;
      msgEl.style.display = 'block';
      setTimeout(() => { msgEl.style.display = 'none'; }, 5000);
    }
  } catch (err) {
    if (msgEl) {
      msgEl.style.color = '#fca5a5';
      msgEl.textContent = `❌ Failed: ${err.message}`;
      msgEl.style.display = 'block';
    }
  }
}

/** Helper: reads current model from the input field and updates the top badge. */
function _refreshGeneratorBadge(provider) {
  const badgeGen = document.getElementById('ui-badge-generator');
  if (!badgeGen) return;
  const colors = { nvidia: '#76d9f5', groq: '#34d399', openrouter: '#818cf8', huggingface: '#fbbf24' };
  const labels = { nvidia: 'NVIDIA', groq: 'Groq', openrouter: 'OpenRouter', huggingface: 'HuggingFace' };
  // Read model from the input that is currently shown on the settings page
  const modelInput = document.getElementById(`${provider}-model-input`);
  const model = modelInput ? modelInput.value.trim() : '';
  badgeGen.textContent = model ? `${labels[provider]} (${model})` : (labels[provider] || provider);
  badgeGen.style.color = colors[provider] || '#fff';
}

/** Read which provider is currently active (from highlighted button). */
function _getActiveProvider() {
  const ids = ['nvidia', 'groq', 'openrouter', 'huggingface'];
  for (const p of ids) {
    const btn = document.getElementById(`prov-btn-${p}`);
    if (btn && btn.classList.contains('provider-active')) return p;
  }
  return null;
}

function saveServerUrl() {
  const url = document.getElementById('server-url-input').value.trim().replace(/\/$/, '');
  if (url) {
    localStorage.setItem('buniyaad_api_url', url);
    document.getElementById('server-url-display').textContent = url;
    showStatusMsg('✅ Backend URL saved!', 'success');
  }
}

async function changePassword() {
  const oldPass = document.getElementById('cp-old').value;
  const newPass = document.getElementById('cp-new').value;
  const msgEl = document.getElementById('cp-msg');
  const btn = document.getElementById('btn-change-password');
  
  if (!oldPass || !newPass) {
    msgEl.textContent = '❌ Please fill both fields';
    msgEl.style.color = '#fca5a5';
    msgEl.style.display = 'block';
    return;
  }
  
  btn.disabled = true;
  btn.textContent = 'Changing...';
  
  try {
    const data = await api('/auth/change-password', 'POST', {
      old_password: oldPass,
      new_password: newPass
    });
    msgEl.textContent = `✅ ${data.message}`;
    msgEl.style.color = '#34d399';
    msgEl.style.display = 'block';
    document.getElementById('cp-old').value = '';
    document.getElementById('cp-new').value = '';
    setTimeout(() => { msgEl.style.display = 'none'; }, 4000);
  } catch (err) {
    msgEl.textContent = `❌ ${err.message}`;
    msgEl.style.color = '#fca5a5';
    msgEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Change Password';
  }
}

async function generateBackupCodes() {
  if (!confirm("Generate new backup codes? Any old codes will stop working immediately.")) return;
  
  try {
    const data = await api('/auth/generate-backup-codes', 'POST');
    const listEl = document.getElementById('backup-codes-list');
    const displayEl = document.getElementById('backup-codes-display');
    
    listEl.innerHTML = data.codes.map((c, i) => `<div>${i+1}. <b>${c}</b></div>`).join('');
    displayEl.style.display = 'block';
    alert(data.message);
  } catch (err) {
    alert(`Failed to generate codes: ${err.message}`);
  }
}

async function saveApiKey(provider) {
  const inputId = `${provider}-key-input`;
  const btnId = `btn-save-${provider}`;
  const key = document.getElementById(inputId).value.trim();

  if (!key) {
    alert('Please enter an API key.');
    return;
  }

  const btn = document.getElementById(btnId);
  btn.textContent = 'Saving...';
  btn.disabled = true;

  const payload = {};
  if (provider === 'openrouter') payload.openrouter_api_key = key;
  if (provider === 'groq') payload.groq_api_key = key;
  if (provider === 'nvidia') payload.nvidia_api_key = key;
  if (provider === 'huggingface') payload.huggingface_api_key = key;

  try {
    const res = await api('/api/settings/keys', 'POST', payload);
    document.getElementById(inputId).value = '';
    alert(res.message);
    loadStatus();
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    btn.textContent = 'Save';
    btn.disabled = false;
  }
}

async function saveModelName(provider) {
  const inputId = `${provider}-model-input`;
  const btnId = `btn-save-${provider}-model`;
  const model = document.getElementById(inputId).value.trim();

  if (!model) {
    alert('Please enter a model name.');
    return;
  }

  const btn = document.getElementById(btnId);
  btn.textContent = 'Saving...';
  btn.disabled = true;

  const payload = {};
  if (provider === 'openrouter') payload.openrouter_model = model;
  if (provider === 'groq') payload.groq_model = model;
  if (provider === 'nvidia') payload.nvidia_model = model;
  if (provider === 'huggingface') payload.huggingface_model = model;

  try {
    await api('/api/settings/keys', 'POST', payload);
    btn.textContent = '✅ Saved';
    setTimeout(() => { btn.textContent = 'Save'; }, 2000);

    // If this is the active provider, update the top badge with the new model
    const activeProvider = _getActiveProvider();
    if (activeProvider === provider) {
      _refreshGeneratorBadge(provider);
    }

    // Also update fact-checker badge if groq model changed
    if (provider === 'groq') {
      const badgeChk = document.getElementById('ui-badge-checker');
      if (badgeChk) badgeChk.textContent = `Groq (${model})`;
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
    btn.textContent = 'Save';
  } finally {
    btn.disabled = false;
  }
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function showStatusMsg(msg, type = 'info') {
  const el = document.getElementById('status-msg');
  if (!el) return;
  el.textContent = msg;
  el.className = `status-message ${type}`;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 6000);
}

async function clearDatabase() {
  if (!confirm("Are you absolutely sure you want to clear the entire database? This cannot be undone.")) return;
  if (!confirm("Final warning: Delete all posts and history?")) return;

  try {
    const res = await api('/api/posts/clear', 'DELETE');
    alert(res.message);
    loadPendingPost();
    loadHistory();
  } catch (err) {
    alert("Error clearing database: " + err.message);
  }
}


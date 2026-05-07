<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CompIntel · AI Research Platform</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --accent:     #e7ff52;
      --accent-ink: #0a0a0b;
      --bg:         #080B0F;
      --surface:    #0C1018;
      --border:     #1A2233;
      --text:       #C8D0DC;
      --dim:        #6A7A90;
      --darker:     #3A4A60;
    }

    html, body {
      height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      -webkit-font-smoothing: antialiased;
    }

    /* Grid texture */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(rgba(30,60,120,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,60,120,0.04) 1px, transparent 1px);
      background-size: 48px 48px;
      pointer-events: none;
      z-index: 0;
    }

    /* ── Top bar ── */
    .topbar {
      position: fixed;
      top: 0; left: 0; right: 0;
      height: 52px;
      background: rgba(8,11,15,0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 2rem;
      z-index: 100;
    }
    .topbar-logo {
      font-family: 'DM Mono', monospace;
      font-size: 0.88rem;
      font-weight: 600;
      color: #fff;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }
    .topbar-logo span { color: var(--accent); }
    .topbar-meta {
      font-family: 'DM Mono', monospace;
      font-size: 0.65rem;
      color: var(--darker);
      letter-spacing: 0.1em;
    }

    /* ── Hero layout ── */
    .hero {
      position: relative;
      z-index: 1;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 80px 1.5rem 3rem;
      text-align: center;
    }

    .hero-eyebrow {
      font-family: 'DM Mono', monospace;
      font-size: 0.68rem;
      color: var(--accent);
      letter-spacing: 0.18em;
      text-transform: uppercase;
      margin-bottom: 1.2rem;
      opacity: 0;
      animation: fadeUp 0.6s ease 0.1s forwards;
    }

    .hero-title {
      font-size: clamp(2.4rem, 6vw, 4.2rem);
      font-weight: 700;
      color: #fff;
      line-height: 1.1;
      letter-spacing: -0.02em;
      margin-bottom: 1.2rem;
      opacity: 0;
      animation: fadeUp 0.6s ease 0.2s forwards;
    }
    .hero-title em {
      font-style: normal;
      color: var(--accent);
    }

    .hero-sub {
      font-size: 1rem;
      color: var(--dim);
      line-height: 1.7;
      max-width: 520px;
      margin-bottom: 2.8rem;
      font-weight: 300;
      opacity: 0;
      animation: fadeUp 0.6s ease 0.3s forwards;
    }

    /* ── Search box ── */
    .search-wrap {
      width: 100%;
      max-width: 560px;
      opacity: 0;
      animation: fadeUp 0.6s ease 0.4s forwards;
    }

    .search-box {
      display: flex;
      gap: 0;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .search-box:focus-within {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(231,255,82,0.08);
    }

    .search-input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      padding: 0.9rem 1.1rem;
      font-family: 'DM Sans', sans-serif;
      font-size: 0.95rem;
      color: #E8EDF5;
    }
    .search-input::placeholder { color: var(--darker); }

    .search-btn {
      background: var(--accent);
      border: none;
      padding: 0 1.4rem;
      cursor: pointer;
      font-family: 'DM Mono', monospace;
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--accent-ink);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      transition: opacity 0.15s;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .search-btn:hover { opacity: 0.88; }
    .search-btn:disabled { opacity: 0.4; cursor: not-allowed; }

    .search-hint {
      margin-top: 0.75rem;
      font-size: 0.75rem;
      color: var(--darker);
      font-family: 'DM Mono', monospace;
    }
    .search-hint span {
      color: var(--dim);
      cursor: pointer;
      transition: color 0.15s;
    }
    .search-hint span:hover { color: var(--accent); }

    /* ── Quick picks ── */
    .quick-picks {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      justify-content: center;
      margin-top: 1rem;
      opacity: 0;
      animation: fadeUp 0.6s ease 0.5s forwards;
    }
    .quick-pick {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 5px 12px;
      font-family: 'DM Mono', monospace;
      font-size: 0.72rem;
      color: var(--dim);
      cursor: pointer;
      transition: all 0.15s;
    }
    .quick-pick:hover {
      border-color: var(--accent);
      color: var(--accent);
      background: rgba(231,255,82,0.04);
    }

    /* ── Feature pills ── */
    .features {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      justify-content: center;
      margin-top: 3.5rem;
      opacity: 0;
      animation: fadeUp 0.6s ease 0.6s forwards;
    }
    .feature-pill {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 100px;
      padding: 6px 14px;
      font-size: 0.78rem;
      color: var(--dim);
    }
    .feature-pill-dot {
      width: 5px; height: 5px;
      border-radius: 50%;
      background: var(--accent);
      flex-shrink: 0;
    }

    /* ── Loading overlay ── */
    .loading-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: var(--bg);
      z-index: 200;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 1.5rem;
    }
    .loading-overlay.visible { display: flex; }

    .loading-logo {
      font-family: 'DM Mono', monospace;
      font-size: 0.9rem;
      font-weight: 600;
      color: #fff;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      margin-bottom: 0.5rem;
    }
    .loading-logo span { color: var(--accent); }

    .loading-steps {
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      width: 320px;
    }
    .loading-step {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-family: 'DM Mono', monospace;
      font-size: 0.75rem;
      color: var(--darker);
      transition: color 0.3s;
    }
    .loading-step.active { color: var(--text); }
    .loading-step.done   { color: var(--darker); }

    .step-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--border);
      flex-shrink: 0;
      transition: background 0.3s;
    }
    .loading-step.active .step-dot { background: #2D7DFF; animation: pulse-dot 1s ease infinite; }
    .loading-step.done   .step-dot { background: #2ED573; }

    @keyframes pulse-dot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%       { opacity: 0.6; transform: scale(0.8); }
    }

    .loading-company {
      font-family: 'DM Mono', monospace;
      font-size: 0.72rem;
      color: var(--accent);
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }

    .loading-bar-wrap {
      width: 320px;
      height: 2px;
      background: var(--border);
      border-radius: 1px;
      overflow: hidden;
      margin-top: 0.5rem;
    }
    .loading-bar {
      height: 100%;
      background: var(--accent);
      border-radius: 1px;
      width: 0%;
      transition: width 0.4s ease;
    }

    /* ── Error toast ── */
    .toast {
      display: none;
      position: fixed;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%);
      background: #1f0a0a;
      border: 1px solid #3a1414;
      border-radius: 6px;
      padding: 0.75rem 1.2rem;
      font-size: 0.84rem;
      color: #FF4757;
      z-index: 300;
      white-space: nowrap;
    }
    .toast.visible { display: block; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(16px); }
      to   { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>

<!-- Top bar -->
<div class="topbar">
  <div class="topbar-logo">◈ COMP<span>INTEL</span></div>
  <div class="topbar-meta">AI RESEARCH PLATFORM · FIVE-AGENT PIPELINE</div>
</div>

<!-- Hero -->
<div class="hero">
  <div class="hero-eyebrow">Competitive Intelligence · Automated</div>
  <h1 class="hero-title">Every company.<br><em>30 seconds.</em></h1>
  <p class="hero-sub">
    Type any company or industry. Five specialized AI agents search the web,
    map competitors, score sentiment, synthesize strategy, and run investment
    signals — all sourced, no hallucination.
  </p>

  <div class="search-wrap">
    <div class="search-box">
      <input
        class="search-input"
        id="search-input"
        type="text"
        placeholder="Company, ticker, or industry — e.g. Apple, NVDA, fintech"
        autocomplete="off"
        spellcheck="false"
      />
      <button class="search-btn" id="search-btn" onclick="runReport()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="5" y1="12" x2="19" y2="12"/>
          <polyline points="12 5 19 12 12 19"/>
        </svg>
        Run Report
      </button>
    </div>
    <div class="search-hint">Try: <span onclick="fillSearch('Apple')">Apple</span> · <span onclick="fillSearch('NVIDIA')">NVIDIA</span> · <span onclick="fillSearch('fintech')">fintech</span> · <span onclick="fillSearch('BMW')">BMW</span></div>
  </div>

  <div class="quick-picks">
    <div class="quick-pick" onclick="fillSearch('Tesla')">TSLA</div>
    <div class="quick-pick" onclick="fillSearch('Microsoft')">MSFT</div>
    <div class="quick-pick" onclick="fillSearch('Amazon')">AMZN</div>
    <div class="quick-pick" onclick="fillSearch('Google')">GOOGL</div>
    <div class="quick-pick" onclick="fillSearch('Meta')">META</div>
    <div class="quick-pick" onclick="fillSearch('Netflix')">NFLX</div>
    <div class="quick-pick" onclick="fillSearch('AI infrastructure')">AI INFRA</div>
    <div class="quick-pick" onclick="fillSearch('fast fashion')">FAST FASHION</div>
  </div>

  <div class="features">
    <div class="feature-pill"><div class="feature-pill-dot"></div>5-agent pipeline</div>
    <div class="feature-pill"><div class="feature-pill-dot"></div>Live web search</div>
    <div class="feature-pill"><div class="feature-pill-dot"></div>Sourced SWOT</div>
    <div class="feature-pill"><div class="feature-pill-dot"></div>Investment strategies</div>
    <div class="feature-pill"><div class="feature-pill-dot"></div>AI analyst chat</div>
    <div class="feature-pill"><div class="feature-pill-dot"></div>PDF export</div>
  </div>
</div>

<!-- Loading overlay -->
<div class="loading-overlay" id="loading-overlay">
  <div class="loading-logo">◈ COMP<span>INTEL</span></div>
  <div class="loading-company" id="loading-company">ANALYZING —</div>
  <div class="loading-steps" id="loading-steps">
    <div class="loading-step" id="step-news">
      <div class="step-dot"></div>Scanning latest news and events
    </div>
    <div class="loading-step" id="step-competitors">
      <div class="step-dot"></div>Identifying key competitors
    </div>
    <div class="loading-step" id="step-sentiment">
      <div class="step-dot"></div>Measuring public perception
    </div>
    <div class="loading-step" id="step-swot">
      <div class="step-dot"></div>Building strategic analysis
    </div>
    <div class="loading-step" id="step-investment">
      <div class="step-dot"></div>Running investment signals
    </div>
  </div>
  <div class="loading-bar-wrap">
    <div class="loading-bar" id="loading-bar"></div>
  </div>
</div>

<!-- Error toast -->
<div class="toast" id="toast"></div>

<script>
  const API_BASE = "http://127.0.0.1:8001";

  const STEPS = ["step-news", "step-competitors", "step-sentiment", "step-swot", "step-investment"];
  let stepIndex  = 0;
  let stepTimer  = null;
  let barPercent = 0;
  let barTimer   = null;

  function fillSearch(text) {
    document.getElementById("search-input").value = text;
    document.getElementById("search-input").focus();
  }

  document.getElementById("search-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") runReport();
  });

  function showToast(msg) {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.classList.add("visible");
    setTimeout(() => t.classList.remove("visible"), 4000);
  }

  function startLoadingUI(company) {
    document.getElementById("loading-company").textContent = `ANALYZING — ${company.toUpperCase()}`;
    document.getElementById("loading-overlay").classList.add("visible");
    stepIndex  = 0;
    barPercent = 0;

    // Animate steps
    STEPS.forEach(id => {
      const el = document.getElementById(id);
      el.classList.remove("active", "done");
    });

    stepTimer = setInterval(() => {
      if (stepIndex < STEPS.length) {
        if (stepIndex > 0) {
          document.getElementById(STEPS[stepIndex - 1]).classList.remove("active");
          document.getElementById(STEPS[stepIndex - 1]).classList.add("done");
        }
        document.getElementById(STEPS[stepIndex]).classList.add("active");
        stepIndex++;
      }
    }, 5000);

    // Animate progress bar (fills to 90% over ~25s, last 10% on completion)
    barTimer = setInterval(() => {
      if (barPercent < 88) {
        barPercent += (88 - barPercent) * 0.035;
        document.getElementById("loading-bar").style.width = barPercent + "%";
      }
    }, 300);
  }

  function finishLoadingUI() {
    clearInterval(stepTimer);
    clearInterval(barTimer);
    // Complete all steps
    STEPS.forEach(id => {
      const el = document.getElementById(id);
      el.classList.remove("active");
      el.classList.add("done");
    });
    document.getElementById("loading-bar").style.width = "100%";
  }

  function stopLoadingUI() {
    clearInterval(stepTimer);
    clearInterval(barTimer);
    document.getElementById("loading-overlay").classList.remove("visible");
  }

  async function runReport() {
    const input   = document.getElementById("search-input");
    const btn     = document.getElementById("search-btn");
    const company = input.value.trim();

    if (!company) {
      showToast("Please enter a company or industry name.");
      input.focus();
      return;
    }

    btn.disabled = true;
    startLoadingUI(company);

    try {
      const res = await fetch(`${API_BASE}/briefing`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ company }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Pipeline failed.");
      }

      const briefing = await res.json();

      finishLoadingUI();

      // Store briefing and redirect to report page
      sessionStorage.setItem("briefing",        JSON.stringify(briefing));
      sessionStorage.setItem("briefing_company", company);

      setTimeout(() => {
        window.location.href = "report.html";
      }, 600);

    } catch (err) {
      stopLoadingUI();
      showToast(`Error: ${err.message}`);
      btn.disabled = false;
    }
  }
</script>
</body>
</html>
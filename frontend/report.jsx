// Report sections — the main CompIntel briefing for NVIDIA (NVDA)
const { useState, useEffect, useRef, useMemo } = React;

// ─────────────────────────────────────────────────────────────────
// Shared atoms
// ─────────────────────────────────────────────────────────────────

const Chip = ({ children, tone = "neutral", className = "" }) => {
  const tones = {
    neutral: "ci-chip-neutral",
    bull: "ci-chip-bull",
    bear: "ci-chip-bear",
    warn: "ci-chip-warn",
    accent: "ci-chip-accent",
    ghost: "ci-chip-ghost",
  };
  return <span className={`ci-chip ${tones[tone]} ${className}`}>{children}</span>;
};

const SectionHeader = ({ num, title, kicker, right }) => (
  <header className="ci-sec-head">
    <div className="ci-sec-head-l">
      <span className="ci-sec-num">{num}</span>
      <div>
        <h2 className="ci-sec-title">{title}</h2>
        {kicker && <p className="ci-sec-kicker">{kicker}</p>}
      </div>
    </div>
    {right && <div className="ci-sec-head-r">{right}</div>}
  </header>
);

const Stat = ({ label, value, sub, tone }) => (
  <div className="ci-stat">
    <div className="ci-stat-label">{label}</div>
    <div className={`ci-stat-value ${tone ? `tone-${tone}` : ""}`}>{value}</div>
    {sub && <div className="ci-stat-sub">{sub}</div>}
  </div>
);

const Source = ({ n, host }) => (
  <a className="ci-src" href="#" onClick={(e) => e.preventDefault()}>
    <span className="ci-src-n">{n}</span>
    <span className="ci-src-host">{host}</span>
  </a>
);

const Bar = ({ value, max = 100, tone = "accent" }) => {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div className={`ci-bar ci-bar-${tone}`}>
      <div className="ci-bar-fill" style={{ width: `${pct}%` }} />
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────
// Top nav
// ─────────────────────────────────────────────────────────────────

const TopNav = ({ activeSection, onJump, ticker, marketStatus }) => {
  const sections = [
    { id: "news", num: "01", label: "News" },
    { id: "competitors", num: "02", label: "Competitors" },
    { id: "sentiment", num: "03", label: "Sentiment" },
    { id: "swot", num: "04", label: "SWOT" },
    { id: "investment", num: "05", label: "Investment" },
  ];
  return (
    <nav className="ci-nav">
      <div className="ci-nav-inner">
        <div className="ci-nav-l">
          <div className="ci-logo">
            <div className="ci-logo-mark" />
            <span className="ci-logo-word">COMPINTEL</span>
          </div>
          <div className="ci-nav-ticker">
            <span className="ci-ticker-sym">{ticker.symbol}</span>
            <span className="ci-ticker-name">{ticker.name}</span>
            <span className={`ci-market ci-market-${marketStatus.kind}`}>
              <span className="ci-market-dot" />
              {marketStatus.label}
            </span>
          </div>
        </div>
        <div className="ci-nav-c">
          {sections.map((s) => (
            <button
              key={s.id}
              className={`ci-nav-link ${activeSection === s.id ? "active" : ""}`}
              onClick={() => onJump(s.id)}
            >
              <span className="ci-nav-link-num">{s.num}</span>
              {s.label}
            </button>
          ))}
        </div>
        <div className="ci-nav-r">
          <button className="ci-btn ci-btn-ghost">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            JSON
          </button>
          <button className="ci-btn ci-btn-primary">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            Export PDF
          </button>
        </div>
      </div>
    </nav>
  );
};

// ─────────────────────────────────────────────────────────────────
// Hero / executive summary
// ─────────────────────────────────────────────────────────────────

const Hero = ({ data }) => (
  <section className="ci-hero" data-screen-label="Hero">
    <div className="ci-hero-meta">
      <Chip tone="accent">FULL BRIEFING</Chip>
      <span className="ci-hero-time">Generated {data.generated} · {data.runtime}s · 5 agents</span>
    </div>
    <div className="ci-hero-grid">
      <div className="ci-hero-l">
        <div className="ci-hero-tag">{data.sector} · {data.industry}</div>
        <h1 className="ci-hero-title">{data.name}</h1>
        <div className="ci-hero-ticker-row">
          <span className="ci-hero-symbol">{data.symbol}</span>
          <span className="ci-hero-exch">NASDAQ</span>
          <span className={`ci-hero-price-delta tone-${data.deltaTone}`}>
            {data.deltaPct > 0 ? "▲" : "▼"} {Math.abs(data.deltaPct).toFixed(2)}%
          </span>
        </div>
        <p className="ci-hero-summary">{data.summary}</p>
      </div>
      <div className="ci-hero-r">
        <div className="ci-hero-price">
          <div className="ci-hero-price-label">LAST</div>
          <div className="ci-hero-price-value">${data.price.toFixed(2)}</div>
          <div className="ci-hero-price-sub">{data.change > 0 ? "+" : ""}${data.change.toFixed(2)} today</div>
        </div>
        <div className="ci-hero-stats">
          <Stat label="MARKET CAP" value={data.marketCap} />
          <Stat label="P/E (TTM)" value={data.pe} />
          <Stat label="52W RANGE" value={data.range} />
          <Stat label="ANALYST" value={data.analyst} tone="bull" />
        </div>
      </div>
    </div>
  </section>
);

// ─────────────────────────────────────────────────────────────────
// 01 — News
// ─────────────────────────────────────────────────────────────────

const NewsSection = ({ items }) => (
  <section className="ci-sec" id="news" data-screen-label="01 News">
    <SectionHeader
      num="01"
      title="Recent Intelligence"
      kicker="Web scan via Tavily · last 30 days"
      right={<Chip tone="ghost">{items.length} signals</Chip>}
    />
    <ol className="ci-news">
      {items.map((it, i) => (
        <li key={i} className="ci-news-item">
          <div className="ci-news-meta">
            <span className="ci-news-date">{it.date}</span>
            <Chip tone={it.tone}>{it.tag}</Chip>
          </div>
          <h3 className="ci-news-title">{it.title}</h3>
          <p className="ci-news-summary">{it.summary}</p>
          <div className="ci-news-srcs">
            {it.sources.map((s, j) => <Source key={j} n={`${i + 1}.${j + 1}`} host={s} />)}
          </div>
        </li>
      ))}
    </ol>
  </section>
);

// ─────────────────────────────────────────────────────────────────
// 02 — Competitors
// ─────────────────────────────────────────────────────────────────

const CompetitorsSection = ({ items }) => (
  <section className="ci-sec" id="competitors" data-screen-label="02 Competitors">
    <SectionHeader
      num="02"
      title="Competitive Landscape"
      kicker="Positioning, pricing signals, recent moves"
      right={<Chip tone="ghost">{items.length} mapped</Chip>}
    />
    <div className="ci-comps">
      {items.map((c, i) => (
        <article key={i} className="ci-comp">
          <div className="ci-comp-head">
            <div className="ci-comp-mark" style={{ background: c.color }}>{c.symbol[0]}</div>
            <div className="ci-comp-id">
              <div className="ci-comp-name">{c.name}</div>
              <div className="ci-comp-sym">{c.symbol} · {c.region}</div>
            </div>
            <div className={`ci-comp-threat tone-${c.threatTone}`}>
              <div className="ci-comp-threat-label">THREAT</div>
              <div className="ci-comp-threat-value">{c.threat}</div>
            </div>
          </div>
          <p className="ci-comp-pos">{c.positioning}</p>
          <dl className="ci-comp-stats">
            <div><dt>SHARE</dt><dd>{c.share}</dd></div>
            <div><dt>PRICING</dt><dd>{c.pricing}</dd></div>
            <div><dt>GROWTH</dt><dd className={`tone-${c.growthTone}`}>{c.growth}</dd></div>
          </dl>
          <div className="ci-comp-move">
            <span className="ci-comp-move-label">LATEST</span>
            <span className="ci-comp-move-text">{c.move}</span>
          </div>
        </article>
      ))}
    </div>
  </section>
);

// ─────────────────────────────────────────────────────────────────
// 03 — Sentiment
// ─────────────────────────────────────────────────────────────────

const SentimentSection = ({ data }) => {
  const score = data.score; // -100..100
  // Place pointer on -100..100 axis
  const pointerPct = ((score + 100) / 200) * 100;
  return (
    <section className="ci-sec" id="sentiment" data-screen-label="03 Sentiment">
      <SectionHeader
        num="03"
        title="Public Sentiment"
        kicker="Reviews, social, press · weighted by recency"
        right={<Chip tone={data.trend === "Improving" ? "bull" : data.trend === "Declining" ? "bear" : "neutral"}>{data.trend}</Chip>}
      />
      <div className="ci-sent">
        <div className="ci-sent-gauge">
          <div className="ci-sent-score-row">
            <div>
              <div className="ci-sent-score-label">SENTIMENT SCORE</div>
              <div className={`ci-sent-score tone-${score > 20 ? "bull" : score < -20 ? "bear" : "neutral"}`}>
                {score > 0 ? "+" : ""}{score}
              </div>
              <div className="ci-sent-score-sub">on a -100 to +100 scale</div>
            </div>
            <div className="ci-sent-legend">
              <span><i className="ci-dot ci-dot-bear" /> Bearish</span>
              <span><i className="ci-dot ci-dot-neutral" /> Neutral</span>
              <span><i className="ci-dot ci-dot-bull" /> Bullish</span>
            </div>
          </div>
          <div className="ci-sent-axis">
            <div className="ci-sent-track" />
            <div className="ci-sent-pointer" style={{ left: `${pointerPct}%` }}>
              <div className="ci-sent-pointer-line" />
              <div className="ci-sent-pointer-bub">{score > 0 ? "+" : ""}{score}</div>
            </div>
            <div className="ci-sent-marks">
              <span>-100</span><span>-50</span><span>0</span><span>+50</span><span>+100</span>
            </div>
          </div>
        </div>
        <ul className="ci-sent-drivers">
          {data.drivers.map((d, i) => (
            <li key={i} className="ci-driver">
              <div className="ci-driver-head">
                <span className={`ci-driver-arrow tone-${d.dir > 0 ? "bull" : "bear"}`}>{d.dir > 0 ? "▲" : "▼"}</span>
                <span className="ci-driver-name">{d.name}</span>
                <span className="ci-driver-strength">{Math.abs(d.dir)}/10</span>
              </div>
              <Bar value={Math.abs(d.dir) * 10} tone={d.dir > 0 ? "bull" : "bear"} />
              <p className="ci-driver-note">{d.note}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};

// ─────────────────────────────────────────────────────────────────
// 04 — SWOT
// ─────────────────────────────────────────────────────────────────

const SWOT_META = {
  S: { tone: "bull", title: "Strengths" },
  W: { tone: "bear", title: "Weaknesses" },
  O: { tone: "accent", title: "Opportunities" },
  T: { tone: "warn", title: "Threats" },
};

const SwotSection = ({ data }) => (
  <section className="ci-sec" id="swot" data-screen-label="04 SWOT">
    <SectionHeader
      num="04"
      title="SWOT Synthesis"
      kicker="Each finding cites its source"
    />
    <div className="ci-swot">
      {(["S", "W", "O", "T"]).map((k) => {
        const meta = SWOT_META[k];
        return (
          <div key={k} className={`ci-swot-q ci-swot-${k}`}>
            <header className="ci-swot-head">
              <span className={`ci-swot-letter tone-${meta.tone}`}>{k}</span>
              <span className="ci-swot-title">{meta.title}</span>
              <span className="ci-swot-count">{data[k].length}</span>
            </header>
            <ul className="ci-swot-list">
              {data[k].map((it, i) => (
                <li key={i}>
                  <p>{it.text}</p>
                  <Source n={`${k}.${i + 1}`} host={it.src} />
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  </section>
);

// ─────────────────────────────────────────────────────────────────
// 05 — Investment
// ─────────────────────────────────────────────────────────────────

const InvestmentSection = ({ data }) => (
  <section className="ci-sec" id="investment" data-screen-label="05 Investment">
    <SectionHeader
      num="05"
      title="Investment Outlook"
      kicker="Bull vs bear · catalysts · three strategies"
      right={<Chip tone={data.signal === "Bullish" ? "bull" : data.signal === "Bearish" ? "bear" : "neutral"}>SIGNAL · {data.signal.toUpperCase()}</Chip>}
    />
    <div className="ci-inv-thesis">
      <div className="ci-thesis ci-thesis-bull">
        <div className="ci-thesis-head"><span className="ci-thesis-tag tone-bull">BULL CASE</span></div>
        <p>{data.bull}</p>
      </div>
      <div className="ci-thesis ci-thesis-bear">
        <div className="ci-thesis-head"><span className="ci-thesis-tag tone-bear">BEAR CASE</span></div>
        <p>{data.bear}</p>
      </div>
    </div>
    <div className="ci-inv-cats">
      <div className="ci-catbox">
        <h4>Key Catalysts</h4>
        <ul>{data.catalysts.map((c, i) => <li key={i}><span className="ci-catbox-arrow">↗</span>{c}</li>)}</ul>
      </div>
      <div className="ci-catbox ci-catbox-risk">
        <h4>Key Risks</h4>
        <ul>{data.risks.map((c, i) => <li key={i}><span className="ci-catbox-arrow">↘</span>{c}</li>)}</ul>
      </div>
    </div>
    <h3 className="ci-strats-title">Three Strategies</h3>
    <div className="ci-strats">
      {data.strategies.map((s, i) => (
        <article key={i} className={`ci-strat ci-strat-${s.style}`}>
          <header className="ci-strat-head">
            <div>
              <div className="ci-strat-num">STRATEGY {String(i + 1).padStart(2, "0")}</div>
              <h4 className="ci-strat-name">{s.name}</h4>
            </div>
            <Chip tone={s.style === "agg" ? "bear" : s.style === "mod" ? "warn" : "bull"}>
              {s.style === "agg" ? "AGGRESSIVE" : s.style === "mod" ? "MODERATE" : "CONSERVATIVE"}
            </Chip>
          </header>
          <p className="ci-strat-signal"><span>ENTRY SIGNAL · </span>{s.signal}</p>
          <dl className="ci-strat-grid">
            <div><dt>ENTRY ZONE</dt><dd>{s.entry}</dd></div>
            <div><dt>TARGET</dt><dd className="tone-bull">{s.target}</dd></div>
            <div><dt>STOP LOSS</dt><dd className="tone-bear">{s.stop}</dd></div>
            <div><dt>POSITION</dt><dd>{s.position}</dd></div>
          </dl>
          <div className="ci-strat-needs">
            <div>
              <div className="ci-strat-needs-h">CATALYSTS NEEDED</div>
              <ul>{s.needs.map((n, j) => <li key={j}>{n}</li>)}</ul>
            </div>
            <div>
              <div className="ci-strat-needs-h">EXIT CONDITIONS</div>
              <ul>{s.exits.map((n, j) => <li key={j}>{n}</li>)}</ul>
            </div>
          </div>
        </article>
      ))}
    </div>
  </section>
);

// ─────────────────────────────────────────────────────────────────
// Footer disclaimer
// ─────────────────────────────────────────────────────────────────

const Foot = () => (
  <footer className="ci-foot">
    <div className="ci-foot-l">
      <span className="ci-foot-mark" />
      <span>COMPINTEL</span>
      <span className="ci-foot-sep">·</span>
      <span>Briefing generated by sequential 5-agent pipeline</span>
    </div>
    <div className="ci-foot-r">
      Not investment advice. Verify all data before trading. Sources cited inline.
    </div>
  </footer>
);

Object.assign(window, {
  TopNav, Hero, NewsSection, CompetitorsSection,
  SentimentSection, SwotSection, InvestmentSection, Foot, Chip,
});

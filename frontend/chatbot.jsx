// Floating CompIntel chatbot — context-aware over the loaded report
const { useState: useS, useEffect: useE, useRef: useR } = React;

const SUGGESTIONS = [
  "Which strategy is best for a beginner?",
  "Explain the P/E ratio",
  "Why is sentiment improving?",
  "What's the biggest risk right now?",
];

const TOOL_STEPS = [
  { label: "Reading executive summary", ms: 600 },
  { label: "Scanning section 03 — Sentiment", ms: 700 },
  { label: "Cross-referencing news + SWOT", ms: 800 },
];

function buildSystemContext(b) {
  return `You are CompIntel's in-report assistant. The user is reading a briefing about ${b.hero.name} (${b.hero.symbol}).
Reference SPECIFIC numbers and findings from this briefing. Keep responses to 2–4 short paragraphs. Use plain English.

Hero: price $${b.hero.price}, market cap ${b.hero.marketCap}, P/E ${b.hero.pe}, analyst ${b.hero.analyst}.
Summary: ${b.hero.summary}
Signal: ${b.investment.signal}.
Bull thesis: ${b.investment.bull}
Bear thesis: ${b.investment.bear}
Sentiment score: ${b.sentiment.score}, trend ${b.sentiment.trend}.
Top competitors: ${b.competitors.map((c) => c.name + " (" + c.threat + ")").join(", ")}.
Strategies: ${b.investment.strategies.map((s) => s.name + " — " + s.entry + " → " + s.target).join(" | ")}.`;
}

const ChatFab = ({ open, onToggle, unread }) => (
  <button className={`ci-fab ${open ? "ci-fab-open" : ""}`} onClick={onToggle} aria-label="Open assistant">
    <span className="ci-fab-pulse" />
    <span className="ci-fab-pulse ci-fab-pulse-2" />
    {open ? (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
        <line x1="6" y1="6" x2="18" y2="18" />
        <line x1="6" y1="18" x2="18" y2="6" />
      </svg>
    ) : (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
    )}
    {unread > 0 && !open && <span className="ci-fab-badge">{unread}</span>}
  </button>
);

const Citation = ({ section }) => {
  const map = {
    "01": { id: "news",        label: "01 News" },
    "02": { id: "competitors", label: "02 Competitors" },
    "03": { id: "sentiment",   label: "03 Sentiment" },
    "04": { id: "swot",        label: "04 SWOT" },
    "05": { id: "investment",  label: "05 Investment" },
  };
  const m = map[section] || { id: "news", label: section };
  const href = "#" + m.id;
  return (
    
      className="ci-cite"
      href={href}
      onClick={(e) => {
        e.preventDefault();
        document.getElementById(m.id) && document.getElementById(m.id).scrollIntoView({ behavior: "smooth", block: "start" });
      }}
    >
      <span className="ci-cite-bracket">[</span>{m.label}<span className="ci-cite-bracket">]</span>
    </a>
  );
};

function renderAssistant(text) {
  const parts = [];
  const re = /\[(0[1-5])\]/g;
  let last = 0, m;
  let key = 0;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(<span key={key++}>{text.slice(last, m.index)}</span>);
    parts.push(<Citation key={key++} section={m[1]} />);
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(<span key={key++}>{text.slice(last)}</span>);
  return parts;
}

const Bubble = ({ msg }) => {
  if (msg.role === "user") {
    return (
      <div className="ci-msg ci-msg-user">
        <div className="ci-msg-body">{msg.text}</div>
      </div>
    );
  }
  if (msg.role === "tool") {
    return (
      <div className="ci-msg ci-msg-tool">
        <span className="ci-tool-spin" />
        <span className="ci-tool-text">{msg.text}</span>
      </div>
    );
  }
  return (
    <div className="ci-msg ci-msg-bot">
      <div className="ci-msg-avatar"><span className="ci-msg-avatar-mark" /></div>
      <div className="ci-msg-body">{renderAssistant(msg.text)}</div>
    </div>
  );
};

const TypingDots = () => (
  <div className="ci-msg ci-msg-bot">
    <div className="ci-msg-avatar"><span className="ci-msg-avatar-mark" /></div>
    <div className="ci-typing"><span /><span /><span /></div>
  </div>
);

const ChatWindow = ({ open, briefing, onClose, apiBase }) => {
  const [messages, setMessages] = useS([
    {
      role: "assistant",
      text:
        `Hi — I've loaded your briefing on ${briefing.hero.name}. Ask me anything about the data in this report. ` +
        `I can explain a concept like the P/E ratio, walk through any of the three strategies in [05], or unpack what's driving the sentiment score in [03].`,
    },
  ]);
  const [draft, setDraft] = useS("");
  const [busy,  setBusy]  = useS(false);
  const [tool,  setTool]  = useS(null);
  const scrollRef = useR(null);
  const inputRef  = useR(null);

  useE(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, busy, tool]);

  useE(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 250);
  }, [open]);

  const send = async (text) => {
    const q = (text ?? draft).trim();
    if (!q || busy) return;
    setDraft("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", text: q }]);

    // Animate tool-use steps while waiting
    let stepIdx = 0;
    const stepTimer = setInterval(() => {
      const step = TOOL_STEPS[stepIdx % TOOL_STEPS.length];
      setTool(step.label);
      stepIdx += 1;
    }, 700);
    setTool(TOOL_STEPS[0].label);

    try {
      // Build conversation history
      const history = messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role, content: m.text }));
      history.push({
        role: "user",
        content:
          q +
          "\n\nWhen citing sections use: [01] News, [02] Competitors, [03] Sentiment, [04] SWOT, [05] Investment — these become clickable chips.",
      });

      const base = apiBase || window.API_BASE || "http://127.0.0.1:8001";

      const res = await fetch(`${base}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company:  briefing.hero.symbol || briefing.hero.name,
          briefing: briefing,
          messages: history,
        }),
      });

      clearInterval(stepTimer);
      setTool(null);

      if (!res.ok) {
        throw new Error(`Server error ${res.status}`);
      }

      // Stream response word by word
      let fullText = "";
      setMessages((m) => [...m, { role: "assistant", text: "" }]);

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();
            if (data === "[DONE]") break;
            try {
              const parsed = JSON.parse(data);
              if (parsed.text) {
                fullText += parsed.text;
                const snapshot = fullText;
                setMessages((m) => {
                  const updated = [...m];
                  updated[updated.length - 1] = { role: "assistant", text: snapshot };
                  return updated;
                });
              }
              if (parsed.error) {
                throw new Error(parsed.error);
              }
            } catch (parseErr) {
              // skip malformed SSE lines
            }
          }
        }
      }
    } catch (e) {
      clearInterval(stepTimer);
      setTool(null);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "I couldn't reach the model just now. Make sure the backend is running and try again." },
      ]);
    }

    setBusy(false);
  };

  return (
    <div className={`ci-chat ${open ? "ci-chat-open" : ""}`} role="dialog" aria-label="CompIntel assistant">
      <header className="ci-chat-head">
        <div className="ci-chat-id">
          <div className="ci-chat-avatar"><span /></div>
          <div>
            <div className="ci-chat-name">CompIntel Assistant</div>
            <div className="ci-chat-status">
              <span className="ci-chat-statdot" />
              Context · {briefing.hero.symbol} briefing
            </div>
          </div>
        </div>
        <div className="ci-chat-acts">
          <button
            className="ci-chat-iconbtn"
            title="New conversation"
            onClick={() => setMessages(messages.slice(0, 1))}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 12a9 9 0 1 0 3-6.7" />
              <polyline points="3 4 3 10 9 10" />
            </svg>
          </button>
          <button className="ci-chat-iconbtn" title="Close" onClick={onClose}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="6" y1="6" x2="18" y2="18" />
              <line x1="6" y1="18" x2="18" y2="6" />
            </svg>
          </button>
        </div>
      </header>

      <div className="ci-chat-scroll" ref={scrollRef}>
        {messages.map((m, i) => <Bubble key={i} msg={m} />)}
        {tool && <Bubble msg={{ role: "tool", text: tool }} />}
        {busy && !tool && <TypingDots />}
      </div>

      {messages.length <= 1 && !busy && (
        <div className="ci-chat-suggest">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="ci-suggest" onClick={() => send(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      <form
        className="ci-chat-input"
        onSubmit={(e) => { e.preventDefault(); send(); }}
      >
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={`Ask about ${briefing.hero.symbol || briefing.hero.name}…`}
          disabled={busy}
        />
        <button
          type="submit"
          disabled={busy || !draft.trim()}
          className="ci-chat-send"
          aria-label="Send"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </button>
      </form>

      <div className="ci-chat-foot">
        <span>Powered by Claude · grounded in your briefing</span>
      </div>
    </div>
  );
};

const Chatbot = ({ briefing, apiBase }) => {
  const [open, setOpen] = useS(false);
  return (
    <>
      <ChatWindow
        open={open}
        briefing={briefing}
        onClose={() => setOpen(false)}
        apiBase={apiBase}
      />
      <ChatFab open={open} onToggle={() => setOpen((o) => !o)} unread={0} />
    </>
  );
};

window.Chatbot = Chatbot;
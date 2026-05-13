import { useEffect, useState } from "react";
import Icon from "../components/Icon";

const SAMPLE_QUESTIONS = [
  "What benefit schemes have we processed?",
  "Show me all employer contribution rates by scheme type",
  "Which schemes have the highest benefit cap?",
  "Compare the premium rates across age bands",
  "What are the deferred periods for income protection schemes?",
  "Which schemes include an Employee Assistance Programme?",
];

const GENIE_URL_STORAGE_KEY = "bpa.genieUrl";

export default function GeniePage() {
  const [genieUrl, setGenieUrl] = useState<string | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [customUrl, setCustomUrl] = useState("");
  const [configSource, setConfigSource] = useState<"server" | "manual" | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch("/api/config/genie");
        if (res.ok) {
          const data = await res.json();
          if (!cancelled && data.url) {
            setGenieUrl(data.url);
            setConfigSource("server");
            return;
          }
        }
      } catch {
        /* ignored — fall through to localStorage */
      }
      if (cancelled) return;
      try {
        const stored = localStorage.getItem(GENIE_URL_STORAGE_KEY);
        if (stored) {
          setGenieUrl(stored);
          setConfigSource("manual");
        }
      } catch {
        /* localStorage unavailable — stay on empty state */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleConnect = () => {
    const trimmed = customUrl.trim();
    if (!trimmed) return;
    setGenieUrl(trimmed);
    setConfigSource("manual");
    setShowConfig(false);
    try {
      localStorage.setItem(GENIE_URL_STORAGE_KEY, trimmed);
    } catch {
      /* storage quota / private mode — keep it only for this session */
    }
  };

  const handleClear = () => {
    setGenieUrl(null);
    setCustomUrl("");
    setConfigSource(null);
    try {
      localStorage.removeItem(GENIE_URL_STORAGE_KEY);
    } catch {
      /* ignored */
    }
  };

  const embedUrl = genieUrl || "";
  const hasUrl = embedUrl.length > 0;

  return (
    <div className="max-w-7xl mx-auto w-full space-y-12">
      <header className="max-w-2xl">
        <span className="inline-flex items-center gap-2 px-3 py-1 bg-secondary-container text-on-secondary-container rounded-sm text-xs font-bold tracking-widest uppercase mb-4 font-label">
          <Icon name="auto_awesome" size={14} />
          Natural Language Querying
        </span>
        <h1 className="font-headline text-5xl text-on-surface tracking-tight mb-4">Genie AI</h1>
        <p className="font-body text-lg text-on-surface-variant leading-relaxed">
          Ask questions about your benefit plan data using natural language. Powered by Databricks Genie.
        </p>
      </header>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setShowConfig(!showConfig)}
          className="flex items-center gap-2 text-on-surface-variant font-label font-medium px-4 py-2 rounded-md bg-surface-container-lowest hover:bg-surface-container-low transition-colors shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)]"
        >
          <Icon name="settings" size={18} />
          {showConfig ? "Hide Config" : "Configure Space"}
        </button>
        {hasUrl && (
          <a
            href={embedUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-secondary font-label font-medium px-4 py-2 rounded-md bg-secondary-container/30 hover:bg-secondary-container/50 transition-colors"
          >
            <Icon name="open_in_new" size={16} />
            Open in Databricks
          </a>
        )}
      </div>

      {showConfig && (
        <div className="bg-surface-container-lowest rounded-xl p-6 shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
          <h3 className="font-headline text-lg text-on-surface mb-2">Genie Space URL</h3>
          <p className="font-body text-sm text-on-surface-variant mb-4">
            Paste the embed URL from your Databricks Genie space. Go to Genie → Share → Embed space.
          </p>
          <div className="flex gap-3">
            <input
              type="url"
              value={customUrl}
              onChange={(e) => setCustomUrl(e.target.value)}
              placeholder="https://e2-demo-field-eng.cloud.databricks.com/genie/rooms/..."
              className="flex-1 bg-surface-container-high border-none border-b-2 border-transparent focus:bg-surface-container-lowest focus:border-secondary rounded px-4 py-2.5 text-sm font-body text-on-surface transition-all focus:ring-0 placeholder:text-on-surface-variant/40"
            />
            <button
              onClick={handleConnect}
              disabled={!customUrl.trim()}
              className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-6 py-2.5 rounded-md font-label text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              Connect
            </button>
            {hasUrl && configSource === "manual" && (
              <button
                onClick={handleClear}
                className="text-on-surface-variant font-label text-sm font-medium px-4 py-2.5 rounded-md hover:bg-surface-container-high transition-colors"
              >
                Clear
              </button>
            )}
          </div>
          {configSource === "server" && (
            <p className="mt-3 text-xs text-on-surface-variant/80 font-body">
              This URL is provided by the deployment config (DATABRICKS_GENIE_SPACE_ID). Pasting a different URL here overrides it for this browser only.
            </p>
          )}
        </div>
      )}

      {hasUrl ? (
        <div className="bg-surface-container-lowest rounded-xl shadow-[0_4px_24px_rgba(26,28,28,0.02)] overflow-hidden">
          <iframe src={embedUrl} allow="clipboard-write" className="w-full border-0" style={{ height: "calc(100vh - 240px)", minHeight: "500px" }} title="Databricks Genie" />
        </div>
      ) : (
        <div className="space-y-8">
          {/* Connect CTA */}
          <div className="bg-surface-container-lowest rounded-xl p-12 text-center shadow-[0_4px_24px_rgba(26,28,28,0.02)] relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-secondary/5 to-transparent opacity-50" />
            <div className="relative">
              <div className="w-24 h-24 rounded-full bg-secondary-container/30 flex items-center justify-center mx-auto mb-6">
                <Icon name="auto_awesome" className="text-secondary" size={40} />
              </div>
              <h3 className="font-headline text-2xl text-on-surface mb-3">Connect a Genie Space</h3>
              <p className="font-body text-sm text-on-surface-variant max-w-md mx-auto mb-6">
                Embed a Databricks Genie space to query your benefit plan data with natural language.
              </p>
              <div className="max-w-md mx-auto mb-6 text-left bg-surface-container-low rounded-lg p-5">
                <p className="font-label text-xs uppercase tracking-wider text-on-surface-variant mb-3">
                  Two ways to connect
                </p>
                <ol className="space-y-3 font-body text-sm text-on-surface">
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary font-label text-xs font-bold flex items-center justify-center">1</span>
                    <span>
                      <span className="font-medium">Create the space once:</span> in Databricks, open <span className="font-mono text-xs">main.bpa_rubjit.benefit_plans_summary</span>, click <span className="font-mono text-xs">Open in</span> → <span className="font-mono text-xs">Genie</span>, save the room, then paste its embed URL via <span className="font-mono text-xs">Configure Space</span> above.
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary font-label text-xs font-bold flex items-center justify-center">2</span>
                    <span>
                      <span className="font-medium">Auto-load for everyone:</span> set the <span className="font-mono text-xs">DATABRICKS_GENIE_SPACE_ID</span> env var in <span className="font-mono text-xs">app.yaml</span> and redeploy. The app will wire the embed URL automatically.
                    </span>
                  </li>
                </ol>
              </div>
              <button
                onClick={() => setShowConfig(true)}
                className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-6 py-2.5 rounded-md font-label font-medium hover:opacity-90 transition-opacity inline-flex items-center gap-2"
              >
                <Icon name="settings" size={16} />
                Configure Space
              </button>
              <div className="flex items-center justify-center gap-2 text-xs text-on-surface-variant bg-surface-container-high/50 rounded-sm px-4 py-2.5 max-w-sm mx-auto mt-6 font-label">
                <Icon name="info" size={14} />
                Requires Genie iframe embed preview enabled in the workspace
              </div>
            </div>
          </div>

          {/* Heritage Insight Card -- uses secondary-container */}
          <div className="bg-secondary-container rounded-xl p-8 relative overflow-hidden">
            <div className="absolute top-4 right-6 text-secondary/10 font-headline text-[80px] font-bold leading-none select-none italic">Q&A</div>
            <div className="relative">
              <h3 className="font-headline text-xl text-on-surface mb-5">Example Questions</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {SAMPLE_QUESTIONS.map((q, i) => (
                  <div key={i} className="flex items-start gap-2.5 px-4 py-3 bg-surface-container-lowest/70 rounded-lg">
                    <Icon name="auto_awesome" className="text-secondary mt-0.5 flex-shrink-0" size={14} />
                    <span className="font-body text-sm text-on-surface/70">{q}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Delta tables */}
          <div className="bg-surface-container-lowest rounded-xl p-7 shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
            <div className="flex justify-between items-end mb-6 border-b border-surface-container-highest pb-4">
              <div>
                <span className="text-xs font-body text-secondary mb-1 block uppercase tracking-wider font-bold">Connected</span>
                <h3 className="font-headline text-xl text-on-surface">Delta Tables</h3>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-surface-container-low rounded-xl p-5">
                <p className="text-xs font-mono text-secondary mb-1.5">main.bpa_rubjit.benefit_plans_summary</p>
                <p className="font-body text-xs text-on-surface-variant">One row per document with pivoted key fields</p>
              </div>
              <div className="bg-surface-container-low rounded-xl p-5">
                <p className="text-xs font-mono text-secondary mb-1.5">main.bpa_rubjit.benefit_plans_detail</p>
                <p className="font-body text-xs text-on-surface-variant">One row per extracted field with confidence scores</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

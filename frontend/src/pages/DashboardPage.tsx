import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Icon from "../components/Icon";
import ExportButton from "../components/ExportButton";
import { useDocumentStore } from "../stores/documentStore";

interface SummaryItem {
  avg_confidence: number;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { documents, volumeFiles, fetchDocuments, fetchVolumeFiles } = useDocumentStore();
  const [summary, setSummary] = useState<SummaryItem[]>([]);
  const [dashboardUrl, setDashboardUrl] = useState<string>("");
  const [powerBiUrl, setPowerBiUrl] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"databricks" | "powerbi">("databricks");

  useEffect(() => {
    fetchDocuments();
    fetchVolumeFiles();
    fetch("/api/export/summary").then((r) => r.json()).then(setSummary).catch(() => {});
    fetch("/api/config/dashboard")
      .then((r) => r.json())
      .then((d) => setDashboardUrl(d?.url || ""))
      .catch(() => {});
    fetch("/api/config/powerbi")
      .then((r) => r.json())
      .then((d) => setPowerBiUrl(d?.url || ""))
      .catch(() => {});
  }, []);

  const approved = documents.filter((d) => d.status === "approved").length;
  const inReview = documents.filter((d) => d.status === "review").length;

  // "Customers with data" counts any customer with at least one document
  // that isn't in an error state — approved, in review, or uploaded all
  // count as data we've touched.
  const customersWithData = new Set(
    documents
      .filter((d) => d.status !== "error")
      .map((d) => volumeFiles.find((f) => f.name === d.filename)?.customer)
      .filter(Boolean)
  ).size;

  const avgConfidenceOverall =
    summary.length > 0
      ? summary.reduce((acc, s) => acc + (Number(s.avg_confidence) || 0), 0) / summary.length
      : 0;

  const tiles = [
    { label: "Approved plans", value: approved, icon: "check_circle" },
    { label: "Customers with data", value: customersWithData, icon: "groups" },
    { label: "Awaiting review", value: inReview, icon: "fact_check" },
    {
      label: "Average confidence",
      value: `${Math.round(avgConfidenceOverall * 100)}%`,
      icon: "insights",
    },
  ];

  return (
    <div className="max-w-6xl mx-auto w-full space-y-10">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="max-w-2xl">
          <h1 className="font-headline text-3xl text-on-surface tracking-tight">Reporting</h1>
          <p className="font-body text-sm text-on-surface-variant mt-1.5">
            Approved benefit plans across your customer portfolio.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate("/genie")}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-surface-container-high/60 bg-white hover:border-outline-variant/40 hover:shadow-sm transition-all font-label text-xs text-on-surface-variant hover:text-on-surface"
          >
            <Icon name="chat" size={15} />
            Ask a question
          </button>
          <ExportButton format="csv" />
          <ExportButton format="json" />
        </div>
      </header>

      {/* Portfolio summary tiles */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {tiles.map((t) => (
          <div
            key={t.label}
            className="bg-white rounded-xl p-5 border border-surface-container-high/60"
          >
            <div className="flex items-center justify-between mb-3">
              <span
                className="w-9 h-9 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: "#45035015" }}
              >
                <span style={{ color: "#450350" }}>
                  <Icon name={t.icon} fill size={18} />
                </span>
              </span>
            </div>
            <div className="font-headline text-3xl text-on-surface">{t.value}</div>
            <div className="font-label text-xs text-on-surface-variant mt-1">{t.label}</div>
          </div>
        ))}
      </section>

      {/* Portfolio insights (embedded BI — Databricks AI/BI + Power BI tabs) */}
      <section className="space-y-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="font-headline text-lg text-on-surface">Portfolio insights</h2>
            <p className="font-body text-xs text-on-surface-variant/70 mt-1">
              Live view of volume, throughput, and extraction quality — available in both Databricks
              AI/BI and Power BI.
            </p>
          </div>
          {activeTab === "databricks" && dashboardUrl && (
            <a
              href={dashboardUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-surface-container-high/60 bg-white hover:border-outline-variant/40 hover:shadow-sm transition-all font-label text-xs text-on-surface-variant hover:text-on-surface"
            >
              <Icon name="open_in_new" size={14} />
              Open in Databricks
            </a>
          )}
          {activeTab === "powerbi" && powerBiUrl && (
            <a
              href={powerBiUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-surface-container-high/60 bg-white hover:border-outline-variant/40 hover:shadow-sm transition-all font-label text-xs text-on-surface-variant hover:text-on-surface"
            >
              <Icon name="open_in_new" size={14} />
              Open in Power BI
            </a>
          )}
        </div>

        {/* Tab switcher */}
        <div className="flex items-center gap-1 border-b border-surface-container-high/60">
          <button
            onClick={() => setActiveTab("databricks")}
            className={`relative px-4 py-2.5 font-label text-xs transition-colors ${
              activeTab === "databricks"
                ? "text-on-surface font-semibold"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            <span className="flex items-center gap-2">
              <Icon name="insights" size={15} />
              Databricks AI/BI
            </span>
            {activeTab === "databricks" && (
              <span
                className="absolute left-0 right-0 -bottom-px h-0.5 rounded-full"
                style={{ backgroundColor: "#450350" }}
              />
            )}
          </button>
          <button
            onClick={() => setActiveTab("powerbi")}
            className={`relative px-4 py-2.5 font-label text-xs transition-colors ${
              activeTab === "powerbi"
                ? "text-on-surface font-semibold"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            <span className="flex items-center gap-2">
              <Icon name="bar_chart" size={15} />
              Power BI
            </span>
            {activeTab === "powerbi" && (
              <span
                className="absolute left-0 right-0 -bottom-px h-0.5 rounded-full"
                style={{ backgroundColor: "#450350" }}
              />
            )}
          </button>
        </div>

        {/* Databricks AI/BI pane */}
        {activeTab === "databricks" &&
          (dashboardUrl ? (
            <div className="bg-white rounded-xl border border-surface-container-high/60 overflow-hidden">
              <iframe
                src={dashboardUrl}
                title="Bulk Purchase Annuity (BPA) · Portfolio Insights"
                allow="clipboard-write"
                className="w-full border-0"
                style={{ height: "calc(100vh - 260px)", minHeight: 620 }}
              />
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-surface-container-high/60 p-12 text-center">
              <div
                className="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4"
                style={{ backgroundColor: "#45035010" }}
              >
                <span style={{ color: "#450350" }}>
                  <Icon name="bar_chart" size={26} />
                </span>
              </div>
              <h3 className="font-headline text-base text-on-surface mb-1.5">
                Dashboard not configured
              </h3>
              <p className="font-body text-xs text-on-surface-variant max-w-sm mx-auto">
                Set <code className="font-mono text-[11px]">DATABRICKS_DASHBOARD_URL</code> in
                app.yaml to embed the Databricks AI/BI dashboard here.
              </p>
            </div>
          ))}

        {/* Power BI pane */}
        {activeTab === "powerbi" &&
          (powerBiUrl ? (
            <div className="bg-white rounded-xl border border-surface-container-high/60 overflow-hidden">
              <iframe
                src={powerBiUrl}
                title="Royal London BPA Dashboard"
                allow="clipboard-write; fullscreen"
                allowFullScreen
                className="w-full border-0"
                style={{ height: "calc(100vh - 260px)", minHeight: 620 }}
              />
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-surface-container-high/60 p-12 text-center">
              <div
                className="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4"
                style={{ backgroundColor: "#F2C81110" }}
              >
                <span style={{ color: "#B8860B" }}>
                  <Icon name="bar_chart" size={26} />
                </span>
              </div>
              <h3 className="font-headline text-base text-on-surface mb-1.5">
                Power BI not configured
              </h3>
              <p className="font-body text-xs text-on-surface-variant max-w-md mx-auto">
                Set <code className="font-mono text-[11px]">POWERBI_EMBED_URL</code> in app.yaml to
                the Power BI "Publish to web" URL (or secure embed URL) that reads from the same
                Unity Catalog Delta tables as the AI/BI dashboard.
              </p>
            </div>
          ))}
      </section>
    </div>
  );
}

import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Icon from "../components/Icon";
import FieldEditor from "../components/FieldEditor";
import StatusBadge from "../components/StatusBadge";
import { useDocumentStore, type ExtractedField } from "../stores/documentStore";

const CATEGORY_LABELS: Record<string, string> = {
  scheme_info: "Scheme Details",
  benefits: "Benefits",
  contributions: "Contributions",
  funding_position: "Funding Position",
  actuarial_assumptions: "Actuarial Assumptions",
  membership: "Membership",
  investment: "Investment Strategy",
  performance: "Investment Performance",
  governance: "Governance",
  exclusions: "Conditions & Caveats",
  ppf: "PPF",
  gmp_equalisation: "GMP Equalisation",
  cashflows: "Cashflows",
  general: "Other",
};

const CATEGORY_ICONS: Record<string, string> = {
  scheme_info: "corporate_fare",
  benefits: "health_and_safety",
  contributions: "payments",
  funding_position: "account_balance",
  actuarial_assumptions: "calculate",
  membership: "groups",
  investment: "trending_up",
  performance: "query_stats",
  governance: "gavel",
  exclusions: "assignment",
  ppf: "policy",
  gmp_equalisation: "balance",
  cashflows: "timeline",
  general: "info",
};

function groupByCategory(fields: ExtractedField[]): Record<string, ExtractedField[]> {
  const groups: Record<string, ExtractedField[]> = {};
  for (const f of fields) {
    const cat = f.field_category || "general";
    if (!groups[cat]) groups[cat] = [];
    groups[cat].push(f);
  }
  return groups;
}

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    documents, currentDocument, fields, loading, volumeFiles,
    fetchDocuments, fetchDocument, fetchFields, updateField, approveAll,
    extractFields, fetchVolumeFiles,
  } = useDocumentStore();
  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>({});
  const [view, setView] = useState<"pdf" | "summary" | "raw">("summary");
  const [autoExtracting, setAutoExtracting] = useState(false);
  const [approving, setApproving] = useState(false);

  const handleApproveAll = async () => {
    if (!id) return;
    setApproving(true);
    try {
      await approveAll(Number(id));
    } finally {
      setApproving(false);
    }
  };

  useEffect(() => { if (!documents.length) fetchDocuments(); }, []);
  useEffect(() => { if (!volumeFiles.length) fetchVolumeFiles(); }, []);
  useEffect(() => {
    if (id) { fetchDocument(Number(id)); fetchFields(Number(id)); }
  }, [id]);

  const customerInfo = (() => {
    if (!currentDocument) return null;
    const vf = volumeFiles.find((f) => f.name === currentDocument.filename);
    if (!vf?.customer) return null;
    return { slug: vf.customer, display: vf.customer_display || vf.customer };
  })();

  // Auto-recover documents that were uploaded but never extracted (e.g. the
  // extract step failed or the app restarted mid-batch). If we land on such
  // a doc, kick off extraction so the user doesn't see an empty panel.
  useEffect(() => {
    if (!id || !currentDocument) return;
    const needsExtract =
      (currentDocument.status === "uploaded" || currentDocument.status === "extracting") &&
      fields.length === 0 &&
      !autoExtracting;
    if (needsExtract) {
      setAutoExtracting(true);
      extractFields(Number(id)).finally(() => setAutoExtracting(false));
    }
  }, [id, currentDocument?.id, currentDocument?.status, fields.length]);

  useEffect(() => {
    if (currentDocument?.file_type === "pdf") setView("pdf");
    else setView("summary");
  }, [currentDocument?.id, currentDocument?.file_type]);

  const grouped = groupByCategory(fields);
  const totalFields = fields.length;
  const approvedFields = fields.filter((f) => f.is_approved).length;
  const progress = totalFields > 0 ? (approvedFields / totalFields) * 100 : 0;
  const toggleCategory = (cat: string) => setCollapsedCategories((p) => ({ ...p, [cat]: !p[cat] }));
  const reviewDocs = documents.filter(
    (d) =>
      d.status === "review" ||
      d.status === "approved" ||
      d.status === "uploaded" ||
      d.status === "extracting",
  );

  /* ---- Document list ---- */
  if (!id) {
    return (
      <div className="max-w-7xl mx-auto w-full space-y-12">
        <header className="max-w-2xl">
          <span className="text-tertiary-container bg-tertiary-fixed/20 px-3 py-1 rounded-sm text-xs font-bold tracking-wider uppercase mb-4 inline-block font-label">
            Review
          </span>
          <h1 className="font-headline text-5xl text-on-surface tracking-tight mb-4">Extraction Review Queue</h1>
          <p className="font-body text-lg text-on-surface-variant leading-relaxed">
            Validate AI-extracted benefit data before approving to the customer record.
          </p>
        </header>

        {reviewDocs.length === 0 && (
          <div className="bg-surface-container-lowest rounded-xl p-14 text-center shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
            <div className="w-16 h-16 bg-surface-container-high/60 rounded-2xl flex items-center justify-center mx-auto mb-5">
              <Icon name="fact_check" className="text-on-surface-variant" size={28} />
            </div>
            <h3 className="font-headline text-xl font-medium text-on-surface mb-2">No documents to review</h3>
            <p className="font-body text-sm text-on-surface-variant max-w-sm mx-auto">
              Process documents from the Ingestion queue first. They will appear here for validation.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reviewDocs.map((doc) => (
            <div
              key={doc.id}
              onClick={() => navigate(`/review/${doc.id}`)}
              className="bg-surface-container-lowest rounded-xl p-6 relative group cursor-pointer hover:-translate-y-1 transition-transform duration-300 shadow-[0_4px_24px_rgba(26,28,28,0.02)]"
            >
              <div className="flex justify-between items-start mb-6">
                <div className="p-3 bg-surface-container-low rounded-lg text-primary">
                  <Icon name="description" size={20} />
                </div>
                <StatusBadge status={doc.status} />
              </div>
              <h4 className="font-headline text-xl text-on-surface mb-2 truncate">{doc.filename}</h4>
              <div className="space-y-1 mb-6">
                <p className="font-body text-sm text-on-surface-variant flex items-center gap-2">
                  <Icon name="folder_open" size={14} /> {doc.file_type.toUpperCase()}
                </p>
                <p className="font-body text-sm text-on-surface-variant flex items-center gap-2">
                  <Icon name="calendar_today" size={14} />
                  {new Date(doc.upload_time).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
                </p>
              </div>
              <div className="pt-4 bg-surface-container-low -mx-6 -mb-6 px-6 py-4 rounded-b-xl flex justify-between items-center">
                {doc.status === "approved" ? (
                  <span className="font-body text-xs text-on-surface-variant">Fully validated</span>
                ) : (
                  <div className="w-full bg-surface-container-highest rounded-full h-1.5 mr-4">
                    <div className="bg-primary h-1.5 rounded-full" style={{ width: "50%" }} />
                  </div>
                )}
                <button className="text-primary hover:text-primary-container font-medium text-sm flex items-center gap-1 font-label flex-shrink-0">
                  {doc.status === "review" ? "Review" : "View"} <Icon name="chevron_right" size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  /* ---- Single document review ---- */
  return (
    <div className="max-w-full">
      {/* Header */}
      <header className="bg-surface-container-lowest/80 backdrop-blur-xl sticky top-16 z-10 px-0 py-5 flex justify-between items-center mb-6 -mt-8 -mx-12 px-12">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate("/review")} className="text-primary hover:text-primary-container p-2 rounded-full hover:bg-surface-container-low transition-colors">
            <Icon name="arrow_back" size={20} />
          </button>
          <div>
            <h1 className="font-headline text-2xl text-primary font-bold tracking-tight">
              {currentDocument?.filename || "Document Review"}
            </h1>
            <div className="flex items-center gap-3 mt-1">
              {currentDocument && <StatusBadge status={currentDocument.status} />}
              <span className="font-body text-sm text-outline font-medium">
                {approvedFields}/{totalFields} fields approved
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {currentDocument?.status === "approved" ? (
            <>
              {customerInfo && (
                <button
                  onClick={() => navigate(`/customers/${customerInfo.slug}`)}
                  className="bg-white border border-primary/30 text-primary px-4 py-2.5 rounded-md font-label font-medium hover:bg-primary/5 transition-colors flex items-center gap-2"
                >
                  <Icon name="arrow_back" size={18} />
                  Back to {customerInfo.display}
                </button>
              )}
              <button
                onClick={() => navigate("/insights")}
                className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-5 py-2.5 rounded-md font-label font-medium shadow-[0_4px_12px_rgba(38,0,45,0.15)] hover:opacity-90 transition-opacity flex items-center gap-2"
              >
                <Icon name="insights" size={18} />
                View reporting
              </button>
            </>
          ) : (
            <>
              <button className="text-primary hover:text-primary-container px-4 py-2 font-label font-medium transition-colors">
                Save Draft
              </button>
              {currentDocument?.status === "review" && (
                <button
                  onClick={handleApproveAll}
                  disabled={loading || approving}
                  aria-busy={approving}
                  className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-6 py-2.5 rounded-md font-label font-medium shadow-[0_4px_12px_rgba(38,0,45,0.15)] hover:opacity-90 transition-opacity flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed min-w-[260px] justify-center"
                >
                  {approving ? (
                    <>
                      <Icon name="sync" size={20} className="animate-spin" />
                      Approving &amp; Syncing...
                    </>
                  ) : (
                    <>
                      <Icon name="done_all" size={20} />
                      Approve &amp; Sync to Catalog
                    </>
                  )}
                </button>
              )}
            </>
          )}
        </div>
      </header>

      {currentDocument?.status === "approved" && (
        <div className="mb-6 rounded-xl border border-primary/20 bg-primary/5 p-5 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <Icon name="verified" size={22} />
            </div>
            <div>
              <div className="font-headline text-base text-on-surface">
                Approved and synced to Unity Catalog
              </div>
              <div className="font-body text-sm text-on-surface-variant">
                All {approvedFields} fields validated. The reporting dashboard will refresh shortly.
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {customerInfo && (
              <button
                onClick={() => navigate(`/customers/${customerInfo.slug}`)}
                className="bg-white border border-primary/30 text-primary px-4 py-2 rounded-md font-label text-sm font-medium hover:bg-primary/5 transition-colors flex items-center gap-2"
              >
                <Icon name="folder_open" size={16} />
                Continue with {customerInfo.display}
              </button>
            )}
            <button
              onClick={() => navigate("/insights")}
              className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-4 py-2 rounded-md font-label text-sm font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
            >
              <Icon name="insights" size={16} />
              View reporting
            </button>
          </div>
        </div>
      )}

      {/* Progress */}
      <div className="w-full h-1 bg-surface-container-highest rounded-full overflow-hidden mb-8">
        <div className="h-full bg-gradient-to-r from-primary to-primary-container rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
      </div>

      {/* Two panels */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: Document viewer */}
        <section className="lg:col-span-5 bg-surface-container-low rounded-xl p-6 relative overflow-hidden flex flex-col" style={{ height: "calc(100vh - 220px)" }}>
          <div className="flex justify-between items-center mb-4 gap-3">
            <h2 className="font-headline text-xl text-primary font-medium">Source Document</h2>
            <div className="inline-flex items-center rounded-full bg-surface-container-lowest border border-surface-container-high/60 p-0.5 text-xs font-label">
              {currentDocument?.file_type === "pdf" && (
                <button
                  onClick={() => setView("pdf")}
                  className={`px-3 py-1 rounded-full transition-colors ${
                    view === "pdf"
                      ? "bg-primary text-on-primary font-medium"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  PDF
                </button>
              )}
              <button
                onClick={() => setView("summary")}
                className={`px-3 py-1 rounded-full transition-colors ${
                  view === "summary"
                    ? "bg-primary text-on-primary font-medium"
                    : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                Summary
              </button>
              <button
                onClick={() => setView("raw")}
                className={`px-3 py-1 rounded-full transition-colors ${
                  view === "raw"
                    ? "bg-primary text-on-primary font-medium"
                    : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                Raw text
              </button>
            </div>
          </div>
          <div className="flex-1 bg-surface-container-lowest rounded-lg overflow-hidden shadow-[0_10px_30px_rgba(26,28,28,0.04)]">
            {view === "pdf" && currentDocument?.file_type === "pdf" && currentDocument?.id ? (
              <iframe
                src={`/api/documents/${currentDocument.id}/source#toolbar=0&navpanes=0`}
                title={currentDocument.filename}
                className="w-full h-full border-0 bg-white"
              />
            ) : view === "raw" ? (
              <div className="w-full h-full overflow-y-auto p-6">
                <pre className="font-body text-xs text-on-surface-variant whitespace-pre-wrap leading-relaxed">
                  {currentDocument?.raw_text || "No raw text available."}
                </pre>
              </div>
            ) : (
              <div className="w-full h-full overflow-y-auto p-6 space-y-6">
                {Object.entries(grouped).map(([cat, catFields]) => (
                  <div key={cat}>
                    <h4 className="font-label text-xs font-semibold text-on-primary-container uppercase tracking-wider mb-3">
                      {CATEGORY_LABELS[cat] || cat}
                    </h4>
                    <div className="space-y-2">
                      {catFields.map((f) => (
                        <div key={f.id} className="flex justify-between text-sm py-1.5 border-b border-surface-container-low/50 last:border-0">
                          <span className="font-body text-on-surface-variant truncate mr-3">{f.field_name}</span>
                          <span className="font-body text-on-surface font-medium text-right flex-shrink-0">{f.extracted_value || "N/A"}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Right: Extraction review */}
        <section className="lg:col-span-7 flex flex-col gap-6 overflow-y-auto pr-2" style={{ maxHeight: "calc(100vh - 220px)" }}>
          <div className="pl-4">
            <h2 className="font-headline text-3xl text-primary font-medium tracking-tight mb-2">Extracted Insights</h2>
            <p className="font-body text-outline font-medium max-w-lg">
              Review and validate the data points identified by the extraction engine.
            </p>
          </div>

          {fields.length === 0 && (
            <div className="bg-surface-container-lowest rounded-xl p-10 flex flex-col items-center justify-center text-center gap-4 shadow-[0_8px_24px_rgba(26,28,28,0.03)]">
              {autoExtracting || loading ? (
                <>
                  <Icon name="sync" size={32} className="text-primary animate-spin" />
                  <div>
                    <h3 className="font-headline text-lg text-on-surface mb-1">
                      Extracting insights...
                    </h3>
                    <p className="font-body text-sm text-on-surface-variant max-w-sm">
                      The AI model is reading the document and pulling out the
                      key benefit data. This usually takes 10-30 seconds.
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <Icon name="auto_awesome" size={32} className="text-on-surface-variant" />
                  <div>
                    <h3 className="font-headline text-lg text-on-surface mb-1">
                      No insights yet
                    </h3>
                    <p className="font-body text-sm text-on-surface-variant max-w-sm mb-4">
                      Extraction hasn't been run for this document. Click below
                      to kick it off.
                    </p>
                    <button
                      onClick={() => {
                        setAutoExtracting(true);
                        extractFields(Number(id)).finally(() => setAutoExtracting(false));
                      }}
                      className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-5 py-2 rounded-md font-label font-medium inline-flex items-center gap-2 hover:opacity-90 transition-opacity"
                    >
                      <Icon name="auto_awesome" size={16} />
                      Run Extraction
                    </button>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Category cards -- bento grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(grouped).map(([cat, catFields]) => {
              const catApproved = catFields.filter((f) => f.is_approved).length;
              const allApproved = catApproved === catFields.length;
              return (
                <div
                  key={cat}
                  className={`bg-surface-container-lowest rounded-xl p-6 shadow-[0_8px_24px_rgba(26,28,28,0.03)] flex flex-col gap-4 ${
                    Object.keys(grouped).length <= 2 ? "md:col-span-2" : ""
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <button
                      onClick={() => toggleCategory(cat)}
                      className="font-headline text-lg text-primary font-medium flex items-center gap-2"
                    >
                      <Icon name={CATEGORY_ICONS[cat] || "info"} className="text-secondary" size={22} />
                      {CATEGORY_LABELS[cat] || cat}
                    </button>
                    <div className={`px-2.5 py-1 rounded-sm font-label text-xs font-semibold flex items-center gap-1 ${
                      allApproved
                        ? "bg-primary/10 text-primary"
                        : "bg-error-container text-on-error-container"
                    }`}>
                      {allApproved ? (
                        <><Icon name="auto_awesome" size={14} /> Verified</>
                      ) : (
                        <>{catApproved}/{catFields.length} Approved</>
                      )}
                    </div>
                  </div>
                  {!collapsedCategories[cat] && (
                    <div className="space-y-2">
                      {catFields.map((f) => <FieldEditor key={f.id} field={f} onUpdate={updateField} />)}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </div>
  );
}

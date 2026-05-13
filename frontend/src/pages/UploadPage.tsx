import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Icon from "../components/Icon";
import StatusBadge from "../components/StatusBadge";
import { useDocumentStore, VolumeFile } from "../stores/documentStore";

const FILE_ICONS: Record<string, { icon: string; color: string; bg: string }> = {
  pdf:  { icon: "picture_as_pdf", color: "text-error",            bg: "bg-error-container/30" },
  xlsx: { icon: "table_view",     color: "text-secondary",        bg: "bg-secondary-container/30" },
  xls:  { icon: "table_view",     color: "text-secondary",        bg: "bg-secondary-container/30" },
  csv:  { icon: "table_view",     color: "text-on-tertiary-container", bg: "bg-tertiary-fixed/30" },
  docx: { icon: "description",    color: "text-primary-container", bg: "bg-primary-fixed/30" },
};

function getFileMeta(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  return FILE_ICONS[ext] ?? FILE_ICONS.pdf;
}

function getFileUploadKey(file: VolumeFile): string {
  return file.relative_path || file.name;
}

// Order matters — more specific patterns must be checked first.
const DOC_TYPE_PATTERNS: Array<[string, string]> = [
  ["benefit_spec", "Benefit Specification"],
  ["bpa_data_pack", "BPA Data Pack"],
  ["summary_funding", "Summary Funding Statement"],
  ["triennial_valuation", "Triennial Valuation"],
  ["funding_update", "Funding Update"],
  ["covenant_review", "Covenant Review"],
  ["trustee_minutes", "Trustee Minutes"],
  ["risk_register", "Risk Register"],
  ["investment_report", "Investment Report"],
  ["asset_allocation", "Asset Allocation"],
  ["ppf_submission", "PPF Submission"],
  ["gmp_equalisation", "GMP Equalisation"],
  ["cashflow_projection", "Cashflow Projection"],
  ["member_data", "Member Data Extract"],
  ["member_options", "Member Options Pack"],
  ["contribution_schedule", "Contribution Schedule"],
  ["sip", "Statement of Investment Principles"],
  ["actuarial", "Actuarial Valuation"],
  ["contribution", "Contribution Schedule"],
];

function docTypeLabel(filename: string): string {
  const name = filename.toLowerCase();
  for (const [pattern, label] of DOC_TYPE_PATTERNS) {
    if (name.includes(pattern)) return label;
  }
  return "Scheme Document";
}

export default function UploadPage() {
  const navigate = useNavigate();
  const {
    documents, volumeFiles, fetchDocuments, fetchVolumeFiles,
    uploadFromVolume, extractFields, loading, error,
  } = useDocumentStore();
  const [processing, setProcessing] = useState<string | null>(null);
  const [batchProcessing, setBatchProcessing] = useState(false);
  const [showCompleted, setShowCompleted] = useState(false);
  const [collapsedCustomers, setCollapsedCustomers] = useState<Record<string, boolean>>({});

  useEffect(() => { fetchDocuments(); fetchVolumeFiles(); }, []);

  const alreadyProcessed = new Set(documents.map((d) => d.filename));
  const newFiles = volumeFiles.filter((f) => !alreadyProcessed.has(f.name));
  const completedFiles = volumeFiles.filter((f) => alreadyProcessed.has(f.name));

  // Group new files by customer
  const grouped = useMemo(() => {
    const groups: Record<string, { display: string; files: VolumeFile[] }> = {};
    for (const f of newFiles) {
      const key = f.customer || "_root";
      const display = f.customer_display || (f.customer ? f.customer : "Uncategorised");
      if (!groups[key]) groups[key] = { display, files: [] };
      groups[key].files.push(f);
    }
    // Sort keys alphabetically, putting root last
    return Object.entries(groups).sort(([a], [b]) => {
      if (a === "_root") return 1;
      if (b === "_root") return -1;
      return a.localeCompare(b);
    });
  }, [newFiles]);

  const toggleCustomer = (key: string) => {
    setCollapsedCustomers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSelectFile = async (file: VolumeFile) => {
    const key = getFileUploadKey(file);
    try {
      setProcessing(file.name);
      const doc = await uploadFromVolume(key);
      await extractFields(doc.id);
      setProcessing(null);
      navigate(`/review/${doc.id}`);
    } catch { setProcessing(null); }
  };

  const handleProcessAll = async () => {
    setBatchProcessing(true);
    for (const file of newFiles) {
      try {
        setProcessing(file.name);
        const doc = await uploadFromVolume(getFileUploadKey(file));
        await extractFields(doc.id);
      } catch { /* continue */ }
    }
    setProcessing(null);
    setBatchProcessing(false);
    await fetchDocuments();
    await fetchVolumeFiles();
  };

  return (
    <div className="max-w-7xl mx-auto w-full space-y-16">
      {/* Hero -- asymmetric layout */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-7 bg-surface-container-low p-10 rounded-xl relative overflow-hidden group">
          <div className="absolute -right-20 -top-20 w-64 h-64 bg-secondary-container/30 rounded-full blur-3xl group-hover:bg-secondary-container/50 transition-colors duration-700" />
          <div className="relative z-10 max-w-lg">
            <span className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary text-xs font-medium rounded-full mb-6 tracking-wide font-label">
              <Icon name="database" size={14} />
              Unity Catalog Sync Active
            </span>
            <h2 className="font-headline text-4xl mb-4 leading-tight text-on-surface">
              Benefit Specifications<br />
              <span className="text-on-surface-variant italic font-light">Pending Extraction</span>
            </h2>
            <p className="font-body text-on-surface-variant leading-relaxed mb-8">
              Scheme documents organised by customer, ready for AI-assisted extraction.
            </p>
            <div className="flex gap-4">
              <button
                onClick={handleProcessAll}
                disabled={batchProcessing || loading || newFiles.length === 0}
                className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-8 py-3 rounded-md font-body font-medium flex items-center gap-2 hover:shadow-[0_10px_40px_-10px_rgba(38,0,45,0.4)] transition-all disabled:opacity-50"
              >
                <Icon name="document_scanner" size={18} />
                {newFiles.length > 1 ? `Process All (${newFiles.length})` : "Trigger AI Extraction"}
              </button>
              <button
                onClick={() => { fetchVolumeFiles(); fetchDocuments(); }}
                disabled={loading}
                className="bg-surface-container-lowest text-on-surface-variant px-4 py-3 rounded-md font-body font-medium hover:bg-surface-container-low transition-colors shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] flex items-center gap-2"
              >
                <Icon name="refresh" className={loading ? "animate-spin" : ""} size={18} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Stats bento */}
        <div className="lg:col-span-5 grid grid-cols-2 gap-4 h-full">
          <div className="bg-surface-container-lowest p-6 rounded-xl flex flex-col justify-between shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
            <Icon name="groups" className="text-primary mb-4" size={24} />
            <div>
              <div className="font-headline text-3xl font-medium mb-1">{grouped.length}</div>
              <div className="font-body text-sm text-on-surface-variant">Customers</div>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-6 rounded-xl flex flex-col justify-between shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
            <Icon name="description" className="text-secondary mb-4" size={24} />
            <div>
              <div className="font-headline text-3xl font-medium mb-1">{newFiles.length}</div>
              <div className="font-body text-sm text-on-surface-variant">New Documents</div>
            </div>
          </div>
        </div>
      </section>

      {error && (
        <div className="p-5 bg-error-container rounded-xl">
          <p className="font-body text-sm text-on-error-container">{error}</p>
        </div>
      )}

      {/* Grouped document list */}
      {grouped.length > 0 && (
        <section className="space-y-10">
          {grouped.map(([key, group]) => {
            const collapsed = collapsedCustomers[key];
            return (
              <div key={key} className="space-y-3">
                {/* Customer header */}
                <button
                  onClick={() => toggleCustomer(key)}
                  className="w-full flex items-center justify-between px-6 py-4 bg-gradient-to-r from-surface-container-low to-surface-container-lowest rounded-xl hover:from-surface-container to-surface-container-low transition-colors group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                      <Icon name="business" size={20} />
                    </div>
                    <div className="text-left">
                      <h3 className="font-headline text-lg text-on-surface">{group.display}</h3>
                      <p className="font-body text-xs text-on-surface-variant mt-0.5">
                        {group.files.length} document{group.files.length === 1 ? "" : "s"} pending
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium font-label">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                      {group.files.length} NEW
                    </span>
                    <Icon
                      name={collapsed ? "chevron_right" : "expand_more"}
                      className="text-on-surface-variant"
                      size={20}
                    />
                  </div>
                </button>

                {/* Customer files */}
                {!collapsed && (
                  <div className="space-y-2 pl-2">
                    {group.files.map((file) => {
                      const meta = getFileMeta(file.name);
                      const isProcessing = processing === file.name;
                      return (
                        <div
                          key={file.relative_path || file.name}
                          className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors duration-200 p-5 rounded-xl flex items-center shadow-[0_2px_12px_rgba(26,28,28,0.02)] group"
                        >
                          <div className="flex-1 flex items-center gap-4 pr-4 min-w-0">
                            <div className={`w-10 h-10 rounded ${meta.bg} flex items-center justify-center ${meta.color} flex-shrink-0`}>
                              <Icon name={meta.icon} size={20} />
                            </div>
                            <div className="min-w-0">
                              <h3 className="font-body font-medium text-on-surface truncate group-hover:text-primary transition-colors">
                                {file.name}
                              </h3>
                              <p className="text-xs text-on-surface-variant mt-0.5">
                                {docTypeLabel(file.name)}
                              </p>
                            </div>
                          </div>
                          <div className="hidden md:block w-24 font-body text-sm text-on-surface-variant">
                            {file.name.split(".").pop()?.toUpperCase()}
                          </div>
                          <div className="hidden md:block w-20 font-body text-sm text-on-surface-variant">
                            {file.size ? `${(file.size / 1024).toFixed(0)} KB` : "--"}
                          </div>
                          <div className="w-28">
                            {isProcessing ? (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm bg-surface-container-high text-on-surface-variant text-xs font-medium">
                                <Icon name="sync" className="animate-spin" size={12} /> Processing
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm bg-secondary-container/50 text-on-secondary-container text-xs font-medium">
                                <span className="w-1.5 h-1.5 rounded-full bg-secondary" /> New
                              </span>
                            )}
                          </div>
                          <div className="w-28 text-right">
                            {!isProcessing && (
                              <button
                                onClick={() => handleSelectFile(file)}
                                disabled={loading || batchProcessing}
                                className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-4 py-2 rounded-md font-label text-xs font-medium hover:opacity-90 transition-opacity disabled:opacity-50 inline-flex items-center gap-1.5"
                              >
                                <Icon name="auto_awesome" size={14} />
                                Extract
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </section>
      )}

      {/* Empty state */}
      {newFiles.length === 0 && !loading && (
        <div className="bg-surface-container-lowest rounded-xl p-14 text-center shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
          <div className="w-16 h-16 bg-secondary-container/30 rounded-2xl flex items-center justify-center mx-auto mb-5">
            <Icon name="inventory_2" className="text-secondary" size={28} />
          </div>
          <h3 className="font-headline text-xl font-medium text-on-surface mb-2">All caught up</h3>
          <p className="font-body text-sm text-on-surface-variant max-w-sm mx-auto">
            No new documents to process. Files added to the Unity Catalog Volume will appear here.
          </p>
        </div>
      )}

      {/* Completed section */}
      {completedFiles.length > 0 && (
        <section>
          <button
            onClick={() => setShowCompleted(!showCompleted)}
            className="flex items-center gap-2 font-body text-sm font-medium text-outline mb-3 hover:text-on-surface transition-colors"
          >
            <Icon name={showCompleted ? "expand_more" : "chevron_right"} size={16} />
            Completed ({completedFiles.length})
          </button>
          {showCompleted && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {completedFiles.map((file) => {
                const meta = getFileMeta(file.name);
                const doc = documents.find((d) => d.filename === file.name);
                return (
                  <div
                    key={file.relative_path || file.name}
                    className="bg-surface-container-lowest rounded-xl p-6 relative group cursor-pointer hover:-translate-y-1 transition-transform duration-300"
                    onClick={() => doc && navigate(`/review/${doc.id}`)}
                  >
                    <div className="flex justify-between items-start mb-6">
                      <div className={`p-3 bg-surface-container-low rounded-lg ${meta.color}`}>
                        <Icon name={meta.icon} size={20} />
                      </div>
                      {doc && <StatusBadge status={doc.status} />}
                    </div>
                    <h4 className="font-headline text-lg text-on-surface mb-2 truncate">{file.name}</h4>
                    <div className="space-y-1 mb-4">
                      {file.customer_display && (
                        <p className="font-body text-sm text-on-surface-variant flex items-center gap-2">
                          <Icon name="business" size={14} /> {file.customer_display}
                        </p>
                      )}
                      <p className="font-body text-sm text-on-surface-variant flex items-center gap-2">
                        <Icon name="folder_open" size={14} /> {docTypeLabel(file.name)}
                      </p>
                      {doc && (
                        <p className="font-body text-sm text-on-surface-variant flex items-center gap-2">
                          <Icon name="calendar_today" size={14} />
                          {new Date(doc.upload_time).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
                        </p>
                      )}
                    </div>
                    <div className="pt-4 bg-surface-container-low -mx-6 -mb-6 px-6 py-4 rounded-b-xl flex justify-between items-center">
                      <span className="font-body text-xs text-on-surface-variant">
                        {file.size ? `${(file.size / 1024).toFixed(0)} KB` : file.name.split(".").pop()?.toUpperCase()}
                      </span>
                      <button className="text-primary hover:text-primary-container font-medium text-sm flex items-center gap-1 font-label">
                        View <Icon name="chevron_right" size={16} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

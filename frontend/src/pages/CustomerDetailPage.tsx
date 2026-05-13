import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import Icon from "../components/Icon";
import StatusBadge from "../components/StatusBadge";
import { getCustomer } from "../data/customers";
import {
  useDocumentStore,
  getCustomerFiles,
  getCustomerDocuments,
  VolumeFile,
  Document,
} from "../stores/documentStore";
import { pushToast } from "../stores/toastStore";

const FILE_ICONS: Record<string, { icon: string; color: string; bg: string }> = {
  pdf: { icon: "picture_as_pdf", color: "text-error", bg: "bg-error-container/30" },
  xlsx: { icon: "table_view", color: "text-secondary", bg: "bg-secondary-container/30" },
  xls: { icon: "table_view", color: "text-secondary", bg: "bg-secondary-container/30" },
  csv: { icon: "table_view", color: "text-on-tertiary-container", bg: "bg-tertiary-fixed/30" },
  docx: { icon: "description", color: "text-primary-container", bg: "bg-primary-fixed/30" },
};

function getFileMeta(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  return FILE_ICONS[ext] ?? FILE_ICONS.pdf;
}

// Order matters — more specific patterns must be checked first (e.g.
// "summary_funding" before "funding_update", "ppf_submission" before "sip").
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

export default function CustomerDetailPage() {
  const { slug = "" } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const customer = getCustomer(slug);

  const {
    documents,
    volumeFiles,
    fetchDocuments,
    fetchVolumeFiles,
    uploadFromVolume,
    extractFields,
    bulkApproveDocuments,
    loading,
    error,
  } = useDocumentStore();

  const [processingFiles, setProcessingFiles] = useState<Set<string>>(new Set());
  const [batchProcessing, setBatchProcessing] = useState(false);
  const [approvingAll, setApprovingAll] = useState(false);
  // Tracks files extracted during this session so their row stays visible
  // with a "Complete" badge instead of disappearing into the In Review list.
  const [completedDocByFilename, setCompletedDocByFilename] = useState<
    Record<string, number>
  >({});

  useEffect(() => {
    fetchDocuments();
    fetchVolumeFiles();
  }, []);

  const { files, docs, pendingFiles, reviewDocs, approvedDocs } = useMemo(() => {
    const files = getCustomerFiles(slug, volumeFiles);
    const docs = getCustomerDocuments(slug, documents, volumeFiles);
    const processedNames = new Set(docs.map((d) => d.filename));
    // A file counts as "pending-or-just-completed" if it is not yet processed,
    // OR it was completed during this session (kept in the list so the user
    // can see it flip from New -> Complete), OR it is currently being
    // processed (so the Processing pill stays visible for the whole ai_extract
    // call even after the underlying document has been inserted).
    const pendingFiles = files.filter(
      (f) =>
        !processedNames.has(f.name) ||
        completedDocByFilename[f.name] != null ||
        processingFiles.has(f.name),
    );
    const completedNames = new Set(Object.keys(completedDocByFilename));
    const reviewDocs = docs.filter(
      (d) =>
        (d.status === "review" || d.status === "uploaded" || d.status === "extracting") &&
        !completedNames.has(d.filename) &&
        !processingFiles.has(d.filename),
    );
    const approvedDocs = docs.filter((d) => d.status === "approved");
    return { files, docs, pendingFiles, reviewDocs, approvedDocs };
  }, [documents, volumeFiles, slug, completedDocByFilename, processingFiles]);

  if (!customer) {
    return (
      <div className="max-w-3xl mx-auto text-center py-20">
        <Icon name="error_outline" size={48} className="text-error mx-auto mb-4" />
        <h2 className="font-headline text-2xl text-on-surface mb-2">Customer not found</h2>
        <p className="font-body text-on-surface-variant mb-6">
          No customer with slug "{slug}" in the registry.
        </p>
        <Link
          to="/customers"
          className="text-primary font-medium text-sm inline-flex items-center gap-1"
        >
          <Icon name="arrow_back" size={16} /> Back to Customers
        </Link>
      </div>
    );
  }

  const total = files.length;
  const approvedCount = approvedDocs.length;
  const progressPct = total === 0 ? 0 : Math.round((approvedCount / total) * 100);
  // Files still needing extraction (excludes ones marked complete this session)
  const trulyPending = pendingFiles.filter(
    (f) => completedDocByFilename[f.name] == null,
  );

  const addProcessing = (name: string) =>
    setProcessingFiles((s) => {
      const next = new Set(s);
      next.add(name);
      return next;
    });
  const removeProcessing = (name: string) =>
    setProcessingFiles((s) => {
      const next = new Set(s);
      next.delete(name);
      return next;
    });

  const handleExtract = async (file: VolumeFile) => {
    const key = file.relative_path || file.name;
    addProcessing(file.name);
    try {
      const doc = await uploadFromVolume(key);
      await extractFields(doc.id);
      setCompletedDocByFilename((prev) => ({ ...prev, [file.name]: doc.id }));
      // If the user is still on this customer page when extraction finishes,
      // jump straight into the review. Otherwise surface a toast from wherever
      // they are now so the work isn't lost.
      if (window.location.pathname.startsWith(`/customers/${slug}`)) {
        navigate(`/review/${doc.id}`);
      } else {
        pushToast({
          title: `${file.name} ready for review`,
          description: "Extraction complete",
          action: { label: "Open review", to: `/review/${doc.id}` },
        });
      }
    } catch {
      // Failed docs are deleted server-side so nothing further to clean up
      // in the UI; we surface a toast in case the user has left the page.
      if (!window.location.pathname.startsWith(`/customers/${slug}`)) {
        pushToast({
          title: `Couldn't extract ${file.name}`,
          description: "The document was removed. Try again from the customer page.",
          tone: "error",
        });
      }
    } finally {
      removeProcessing(file.name);
    }
  };

  const handleApproveAllInReview = async () => {
    const ids = reviewDocs.map((d) => d.id);
    if (!ids.length) return;
    setApprovingAll(true);
    try {
      await bulkApproveDocuments(ids);
    } finally {
      setApprovingAll(false);
    }
  };

  const handleExtractAll = async () => {
    setBatchProcessing(true);
    const toProcess = pendingFiles.filter(
      (f) => completedDocByFilename[f.name] == null,
    );
    for (const file of toProcess) {
      addProcessing(file.name);
      try {
        const doc = await uploadFromVolume(file.relative_path || file.name);
        await extractFields(doc.id);
        setCompletedDocByFilename((prev) => ({ ...prev, [file.name]: doc.id }));
      } catch {
        // Swallow per-file errors so the batch keeps moving. Failed docs are
        // deleted server-side so they never surface as "error" rows in the UI.
      } finally {
        removeProcessing(file.name);
      }
    }
    setBatchProcessing(false);
    await fetchDocuments();
    await fetchVolumeFiles();
  };

  return (
    <div className="max-w-7xl mx-auto w-full space-y-8">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 font-body text-sm text-on-surface-variant">
        <Link to="/customers" className="hover:text-primary transition-colors flex items-center gap-1">
          <Icon name="arrow_back" size={16} />
          Customers
        </Link>
        <Icon name="chevron_right" size={14} className="opacity-40" />
        <span className="text-on-surface font-medium">{customer.display}</span>
      </nav>

      {/* Hero */}
      <section className="bg-surface-container-low rounded-xl p-10 relative overflow-hidden">
        <div className="absolute -right-20 -top-20 w-64 h-64 bg-primary/5 rounded-full blur-3xl" />
        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-7">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                <Icon name={customer.sector_icon} size={24} />
              </div>
              <span className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary text-xs font-medium rounded-full tracking-wide font-label">
                {customer.sector}
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1 bg-surface-container-high text-on-surface-variant text-xs font-medium rounded-full tracking-wide font-label">
                {customer.status}
              </span>
            </div>
            <h1 className="font-headline text-3xl leading-tight text-on-surface mb-3">
              {customer.display}
            </h1>
            <div className="flex flex-wrap items-center gap-x-6 gap-y-2 font-body text-sm text-on-surface-variant">
              <span className="flex items-center gap-1.5">
                <Icon name="savings" size={16} /> GBP {customer.scheme_size_m}m scheme
              </span>
              <span className="flex items-center gap-1.5">
                <Icon name="group" size={16} /> {customer.member_count.toLocaleString("en-GB")} members
              </span>
              <span className="flex items-center gap-1.5">
                <Icon name="payments" size={16} /> GBP {customer.transaction_m}m indicative transaction
              </span>
            </div>
          </div>

          <div className="lg:col-span-5 bg-white rounded-xl p-6 shadow-[0_4px_24px_rgba(26,28,28,0.04)]">
            <div className="flex items-baseline justify-between mb-3">
              <div>
                <div className="font-headline text-3xl text-on-surface">
                  {approvedCount}
                  <span className="text-on-surface-variant/60 text-xl font-normal"> / {total}</span>
                </div>
                <div className="font-body text-xs text-on-surface-variant mt-0.5">
                  Documents approved
                </div>
              </div>
              <span className="font-label text-sm text-primary font-medium">{progressPct}%</span>
            </div>
            <div className="h-2 bg-surface-container-high rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary to-primary-container transition-all"
                style={{ width: `${progressPct}%` }}
              />
            </div>
            {trulyPending.length > 0 && (
              <button
                onClick={handleExtractAll}
                disabled={batchProcessing || loading}
                className="mt-5 w-full bg-gradient-to-r from-primary to-primary-container text-on-primary py-2.5 rounded-md font-body font-medium flex items-center justify-center gap-2 hover:shadow-[0_10px_40px_-10px_rgba(69,3,80,0.4)] transition-all disabled:opacity-50"
              >
                <Icon name="auto_awesome" size={18} />
                {batchProcessing ? "Extracting..." : `Extract All Pending (${trulyPending.length})`}
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Stats strip */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard icon="description" label="Total" value={total} tone="neutral" />
        <StatCard icon="hourglass_empty" label="Pending" value={trulyPending.length} tone="tertiary" />
        <StatCard icon="fact_check" label="In Review" value={reviewDocs.length + Object.keys(completedDocByFilename).length} tone="secondary" />
        <StatCard icon="verified" label="Approved" value={approvedCount} tone="primary" />
      </section>

      {error && (
        <div className="p-5 bg-error-container rounded-xl">
          <p className="font-body text-sm text-on-error-container">{error}</p>
        </div>
      )}

      {/* Document sections */}
      <DocumentSection
        title="Pending Extraction"
        icon="upload_file"
        emptyLabel="All documents have been extracted."
        count={pendingFiles.length}
      >
        {pendingFiles.map((file) => {
          const completedId = completedDocByFilename[file.name];
          return (
            <PendingRow
              key={file.relative_path || file.name}
              file={file}
              isProcessing={processingFiles.has(file.name)}
              disabled={loading || batchProcessing}
              isComplete={completedId != null}
              onExtract={() => handleExtract(file)}
              onReview={() =>
                completedId != null && navigate(`/review/${completedId}`)
              }
            />
          );
        })}
      </DocumentSection>

      <DocumentSection
        title="In Review"
        icon="fact_check"
        emptyLabel="No documents awaiting review."
        count={reviewDocs.length}
        action={
          reviewDocs.length > 0 ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleApproveAllInReview();
              }}
              disabled={approvingAll || loading}
              className="inline-flex items-center gap-1.5 bg-gradient-to-r from-primary to-primary-container text-on-primary px-3 py-1.5 rounded-md font-label text-xs font-medium hover:opacity-90 transition-opacity disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {approvingAll ? (
                <>
                  <Icon name="sync" size={14} className="animate-spin" />
                  Approving {reviewDocs.length}...
                </>
              ) : (
                <>
                  <Icon name="done_all" size={14} />
                  Approve all ({reviewDocs.length})
                </>
              )}
            </button>
          ) : null
        }
      >
        {reviewDocs.map((doc) => (
          <DocRow
            key={doc.id}
            doc={doc}
            cta="Review"
            onClick={() => navigate(`/review/${doc.id}`)}
          />
        ))}
      </DocumentSection>

      <DocumentSection
        title="Approved"
        icon="verified"
        emptyLabel="No approved documents yet."
        count={approvedDocs.length}
      >
        {approvedDocs.map((doc) => (
          <DocRow
            key={doc.id}
            doc={doc}
            cta="View"
            onClick={() => navigate(`/review/${doc.id}`)}
          />
        ))}
      </DocumentSection>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  tone,
}: {
  icon: string;
  label: string;
  value: number;
  tone: "primary" | "secondary" | "tertiary" | "neutral";
}) {
  const color =
    tone === "primary"
      ? "text-primary"
      : tone === "secondary"
      ? "text-secondary"
      : tone === "tertiary"
      ? "text-on-tertiary-container"
      : "text-on-surface-variant";
  return (
    <div className="bg-surface-container-lowest p-5 rounded-xl shadow-[0_2px_12px_rgba(26,28,28,0.02)]">
      <Icon name={icon} size={20} className={`${color} mb-3`} />
      <div className="font-headline text-2xl text-on-surface">{value}</div>
      <div className="font-body text-xs text-on-surface-variant mt-0.5">{label}</div>
    </div>
  );
}

function DocumentSection({
  title,
  icon,
  count,
  emptyLabel,
  defaultOpen = true,
  action,
  children,
}: {
  title: string;
  icon: string;
  count: number;
  emptyLabel: string;
  defaultOpen?: boolean;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section>
      <div className="flex items-center gap-3 mb-3 group">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          className="flex items-center gap-3 flex-1 text-left select-none"
        >
          <Icon
            name="expand_more"
            size={18}
            className={`text-on-surface-variant transition-transform duration-300 ease-out ${
              open ? "rotate-0" : "-rotate-90"
            }`}
          />
          <Icon name={icon} size={18} className="text-on-surface-variant" />
          <h3 className="font-headline text-lg text-on-surface group-hover:text-primary transition-colors">
            {title}
          </h3>
          <span className="font-label text-xs text-on-surface-variant bg-surface-container-high/60 px-2 py-0.5 rounded-full">
            {count}
          </span>
        </button>
        {action}
      </div>
      <div
        className={`grid transition-[grid-template-rows,opacity] duration-300 ease-out ${
          open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">
          {count === 0 ? (
            <div className="bg-surface-container-lowest rounded-xl px-6 py-5 text-sm font-body text-on-surface-variant/70 italic">
              {emptyLabel}
            </div>
          ) : (
            <div className="space-y-2">{children}</div>
          )}
        </div>
      </div>
    </section>
  );
}

function PendingRow({
  file,
  isProcessing,
  disabled,
  isComplete,
  onExtract,
  onReview,
}: {
  file: VolumeFile;
  isProcessing: boolean;
  disabled: boolean;
  isComplete: boolean;
  onExtract: () => void;
  onReview: () => void;
}) {
  const meta = getFileMeta(file.name);
  return (
    <div className="bg-surface-container-lowest hover:bg-surface-container-low transition-colors p-5 rounded-xl flex items-center gap-4 shadow-[0_2px_12px_rgba(26,28,28,0.02)]">
      <div className={`w-10 h-10 rounded ${meta.bg} flex items-center justify-center ${meta.color} flex-shrink-0`}>
        <Icon name={meta.icon} size={20} />
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-body font-medium text-on-surface truncate">{file.name}</h4>
        <p className="text-xs text-on-surface-variant mt-0.5">{docTypeLabel(file.name)}</p>
      </div>
      <div className="hidden md:block w-20 font-body text-xs text-on-surface-variant">
        {file.size ? `${(file.size / 1024).toFixed(0)} KB` : "--"}
      </div>
      <div className="w-28">
        {isProcessing ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm bg-surface-container-high text-on-surface-variant text-xs font-medium">
            <Icon name="sync" className="animate-spin" size={12} /> Processing
          </span>
        ) : isComplete ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm bg-primary/10 text-primary text-xs font-medium">
            <Icon name="check_circle" size={12} /> Complete
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm bg-secondary-container/50 text-on-secondary-container text-xs font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary" /> New
          </span>
        )}
      </div>
      {!isProcessing && (
        isComplete ? (
          <button
            onClick={onReview}
            className="bg-white border border-primary/30 text-primary px-4 py-2 rounded-md font-label text-xs font-medium hover:bg-primary/5 transition-colors inline-flex items-center gap-1.5 flex-shrink-0"
          >
            Review
            <Icon name="chevron_right" size={14} />
          </button>
        ) : (
          <button
            onClick={onExtract}
            disabled={disabled}
            className="bg-gradient-to-r from-primary to-primary-container text-on-primary px-4 py-2 rounded-md font-label text-xs font-medium hover:opacity-90 transition-opacity disabled:opacity-50 inline-flex items-center gap-1.5 flex-shrink-0"
          >
            <Icon name="auto_awesome" size={14} />
            Extract
          </button>
        )
      )}
    </div>
  );
}

function DocRow({
  doc,
  cta,
  onClick,
}: {
  doc: Document;
  cta: string;
  onClick: () => void;
}) {
  const meta = getFileMeta(doc.filename);
  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-surface-container-lowest hover:bg-surface-container-low transition-colors p-5 rounded-xl flex items-center gap-4 shadow-[0_2px_12px_rgba(26,28,28,0.02)] group"
    >
      <div className={`w-10 h-10 rounded ${meta.bg} flex items-center justify-center ${meta.color} flex-shrink-0`}>
        <Icon name={meta.icon} size={20} />
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-body font-medium text-on-surface truncate group-hover:text-primary transition-colors">
          {doc.filename}
        </h4>
        <p className="text-xs text-on-surface-variant mt-0.5">{docTypeLabel(doc.filename)}</p>
      </div>
      <div className="hidden md:block font-body text-xs text-on-surface-variant">
        {new Date(doc.upload_time).toLocaleDateString("en-GB", {
          day: "numeric",
          month: "short",
          year: "numeric",
        })}
      </div>
      <StatusBadge status={doc.status} />
      <span className="text-primary font-label text-xs font-medium inline-flex items-center gap-1 flex-shrink-0">
        {cta}
        <Icon name="chevron_right" size={14} />
      </span>
    </button>
  );
}

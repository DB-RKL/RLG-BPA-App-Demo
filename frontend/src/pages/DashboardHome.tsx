import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Icon from "../components/Icon";
import StatusBadge from "../components/StatusBadge";
import { useDocumentStore, getCustomerFiles, getCustomerDocuments } from "../stores/documentStore";
import { CUSTOMERS, getCustomer } from "../data/customers";

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

function formatWhen(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs} hr${hrs > 1 ? "s" : ""} ago`;
  const days = Math.round(hrs / 24);
  if (days < 7) return `${days} day${days > 1 ? "s" : ""} ago`;
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

export default function DashboardHome() {
  const navigate = useNavigate();
  const { documents, volumeFiles, fetchDocuments, fetchVolumeFiles } = useDocumentStore();

  useEffect(() => {
    fetchDocuments();
    fetchVolumeFiles();
  }, []);

  const processedNames = new Set(documents.map((d) => d.filename));
  const newFiles = volumeFiles.filter((f) => !processedNames.has(f.name));
  const inReviewDocs = documents.filter((d) => d.status === "review");
  const newCount = newFiles.length;
  const reviewCount = inReviewDocs.length;
  const pending = newCount + reviewCount;

  // Customers with outstanding work
  const customerSummaries = CUSTOMERS.map((c) => {
    const cFiles = getCustomerFiles(c.slug, volumeFiles);
    const cDocs = getCustomerDocuments(c.slug, documents, volumeFiles);
    const total = cFiles.length;
    const approved = cDocs.filter((d) => d.status === "approved").length;
    const review = cDocs.filter((d) => d.status === "review").length;
    const pend = total - cDocs.filter((d) => d.status === "approved" || d.status === "review").length;
    const progress = total > 0 ? Math.round((approved / total) * 100) : 0;
    return {
      ...c,
      total,
      approved,
      review,
      pending: pend,
      progress,
      outstanding: review + pend,
    };
  });

  const customersWithWork = customerSummaries
    .filter((c) => c.outstanding > 0 || c.total > 0)
    .sort((a, b) => b.outstanding - a.outstanding || b.total - a.total)
    .slice(0, 6);

  // Recent work: most recent documents, enriched with customer name
  const recentDocs = [...documents]
    .sort((a, b) => new Date(b.upload_time).getTime() - new Date(a.upload_time).getTime())
    .slice(0, 3)
    .map((doc) => {
      const vf = volumeFiles.find((f) => f.name === doc.filename);
      const customer = vf?.customer ? getCustomer(vf.customer) : undefined;
      return { doc, customer };
    });

  const topReview = inReviewDocs[0];

  const openDoc = (docId: number, status: string, customerSlug?: string) => {
    if (status === "review" || status === "approved") {
      navigate(`/review/${docId}`);
    } else if (customerSlug) {
      navigate(`/customers/${customerSlug}`);
    } else {
      navigate("/customers");
    }
  };

  const primaryCta = reviewCount > 0
    ? { label: "Continue reviewing", action: () => topReview && navigate(`/review/${topReview.id}`) }
    : newCount > 0
    ? { label: "Start on new documents", action: () => navigate("/customers") }
    : null;

  return (
    <div className="max-w-6xl mx-auto w-full space-y-10">
      {/* Greeting */}
      <section className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="font-headline text-3xl text-on-surface tracking-tight">
            {getGreeting()}
          </h1>
          <p className="font-body text-sm text-on-surface-variant mt-1.5">
            {pending > 0 ? (
              <>
                You have{" "}
                <span className="font-medium text-on-surface">{pending}</span>{" "}
                document{pending > 1 ? "s" : ""} waiting
                {customersWithWork.length > 0 && (
                  <>
                    {" "}across{" "}
                    <span className="font-medium text-on-surface">{customersWithWork.length}</span>{" "}
                    customer{customersWithWork.length > 1 ? "s" : ""}
                  </>
                )}
                .
              </>
            ) : (
              "You're all caught up."
            )}
          </p>
        </div>
        {primaryCta && (
          <button
            onClick={primaryCta.action}
            className="flex items-center gap-2 text-white px-5 py-2.5 rounded-lg font-label text-sm font-medium hover:opacity-90 transition-opacity shrink-0"
            style={{ backgroundColor: "#450350" }}
          >
            <Icon name="arrow_forward" size={18} />
            {primaryCta.label}
          </button>
        )}
      </section>

      {/* Pick up where you left off */}
      {recentDocs.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-headline text-lg text-on-surface">Pick up where you left off</h2>
            <button
              onClick={() => navigate("/review")}
              className="font-label text-xs text-on-surface-variant/70 hover:text-on-surface transition-colors"
            >
              See all activity
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentDocs.map(({ doc, customer }) => (
              <button
                key={doc.id}
                onClick={() => openDoc(doc.id, doc.status, customer?.slug)}
                className="bg-white rounded-xl border border-surface-container-high/60 p-5 text-left hover:border-outline-variant/40 hover:shadow-sm transition-all group"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 min-w-0">
                    <Icon
                      name={customer?.sector_icon || "description"}
                      className="text-on-surface-variant/60 flex-shrink-0"
                      size={16}
                    />
                    <span className="font-label text-xs text-on-surface-variant truncate">
                      {customer?.display || "Uncategorised"}
                    </span>
                  </div>
                  <StatusBadge status={doc.status} />
                </div>
                <p className="font-body text-sm font-medium text-on-surface leading-snug line-clamp-2 mb-4">
                  {doc.filename}
                </p>
                <div className="flex items-center justify-between">
                  <span className="font-body text-[11px] text-on-surface-variant/70">
                    {formatWhen(doc.upload_time)}
                  </span>
                  <span className="flex items-center gap-1 font-label text-[11px] text-on-surface-variant/0 group-hover:text-on-surface-variant transition-colors">
                    Open
                    <Icon name="arrow_forward" size={12} />
                  </span>
                </div>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Needs your attention */}
      <section>
        <h2 className="font-headline text-lg text-on-surface mb-4">Needs your attention</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate("/review")}
            disabled={reviewCount === 0}
            className="bg-white rounded-xl border border-surface-container-high/60 p-6 text-left hover:border-outline-variant/40 hover:shadow-sm transition-all group disabled:opacity-60 disabled:cursor-default disabled:hover:border-surface-container-high/60 disabled:hover:shadow-none"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: "#45035015" }}>
                <span style={{ color: "#450350" }}>
                  <Icon name="fact_check" fill size={20} />
                </span>
              </div>
              <Icon name="arrow_forward" className="text-outline-variant/0 group-hover:text-on-surface-variant transition-all" size={16} />
            </div>
            <div className="font-headline text-3xl text-on-surface">{reviewCount}</div>
            <div className="font-label text-sm text-on-surface-variant mt-1">Documents to review</div>
            <div className="font-body text-xs text-on-surface-variant/60 mt-2">
              {reviewCount > 0 ? "Check the AI extractions and approve" : "Nothing in the review queue"}
            </div>
          </button>

          <button
            onClick={() => navigate("/customers")}
            disabled={newCount === 0}
            className="bg-white rounded-xl border border-surface-container-high/60 p-6 text-left hover:border-outline-variant/40 hover:shadow-sm transition-all group disabled:opacity-60 disabled:cursor-default disabled:hover:border-surface-container-high/60 disabled:hover:shadow-none"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: "#45035015" }}>
                <span style={{ color: "#450350" }}>
                  <Icon name="inbox" fill size={20} />
                </span>
              </div>
              <Icon name="arrow_forward" className="text-outline-variant/0 group-hover:text-on-surface-variant transition-all" size={16} />
            </div>
            <div className="font-headline text-3xl text-on-surface">{newCount}</div>
            <div className="font-label text-sm text-on-surface-variant mt-1">New documents</div>
            <div className="font-body text-xs text-on-surface-variant/60 mt-2">
              {newCount > 0 ? "Fresh files ready to be processed" : "No new documents waiting"}
            </div>
          </button>
        </div>
      </section>

      {/* Your customers */}
      {customersWithWork.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-headline text-lg text-on-surface">Your customers</h2>
            <button
              onClick={() => navigate("/customers")}
              className="font-label text-xs text-on-surface-variant/70 hover:text-on-surface transition-colors"
            >
              View all customers
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {customersWithWork.map((c) => (
              <button
                key={c.slug}
                onClick={() => navigate(`/customers/${c.slug}`)}
                className="bg-white rounded-xl border border-surface-container-high/60 p-5 text-left hover:border-outline-variant/40 hover:shadow-sm transition-all group"
              >
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="min-w-0 flex-1">
                    <p className="font-body text-sm font-medium text-on-surface leading-snug line-clamp-2">
                      {c.display}
                    </p>
                    <span className="inline-flex items-center gap-1 mt-1.5 font-label text-[10px] text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                      <Icon name={c.sector_icon} size={10} />
                      {c.sector}
                    </span>
                  </div>
                </div>

                <div className="mt-4">
                  <div className="flex items-center justify-between text-[11px] font-label text-on-surface-variant mb-1.5">
                    <span>Progress</span>
                    <span className="text-on-surface">{c.progress}%</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-surface-container-high/60 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${c.progress}%`, backgroundColor: "#450350" }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between mt-3">
                  <span className="font-body text-[11px] text-on-surface-variant/80">
                    {c.outstanding > 0
                      ? `${c.outstanding} awaiting${c.review > 0 ? " review" : ""}`
                      : "All up to date"}
                  </span>
                  <span className="flex items-center gap-1 font-label text-[11px] text-on-surface-variant/0 group-hover:text-on-surface-variant transition-colors">
                    Open
                    <Icon name="arrow_forward" size={12} />
                  </span>
                </div>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Quick actions */}
      <section className="flex flex-wrap gap-2 pt-2">
        {[
          { label: "Open customers", link: "/customers", icon: "groups" },
          { label: "Review queue", link: "/review", icon: "fact_check" },
          { label: "Reporting", link: "/insights", icon: "insights" },
          { label: "Ask a question", link: "/genie", icon: "chat" },
        ].map((item) => (
          <button
            key={item.label}
            onClick={() => navigate(item.link)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-surface-container-high/60 bg-white hover:border-outline-variant/40 hover:shadow-sm transition-all font-label text-xs text-on-surface-variant hover:text-on-surface"
          >
            <Icon name={item.icon} size={15} />
            {item.label}
          </button>
        ))}
      </section>
    </div>
  );
}

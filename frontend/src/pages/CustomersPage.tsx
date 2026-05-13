import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import Icon from "../components/Icon";
import { CUSTOMERS, CustomerMeta } from "../data/customers";
import {
  useDocumentStore,
  getCustomerFiles,
  getCustomerDocuments,
} from "../stores/documentStore";

interface CustomerStats {
  customer: CustomerMeta;
  total: number;
  pending: number;
  inReview: number;
  approved: number;
  progressPct: number;
}

function formatMoney(m: number): string {
  return `GBP ${m.toFixed(0)}m`;
}

function formatMembers(n: number): string {
  return `${n.toLocaleString("en-GB")} members`;
}

export default function CustomersPage() {
  const navigate = useNavigate();
  const {
    documents,
    volumeFiles,
    fetchDocuments,
    fetchVolumeFiles,
    loading,
    error,
  } = useDocumentStore();

  useEffect(() => {
    fetchDocuments();
    fetchVolumeFiles();
  }, []);

  const stats: CustomerStats[] = useMemo(() => {
    return CUSTOMERS.map((c) => {
      const files = getCustomerFiles(c.slug, volumeFiles);
      const docs = getCustomerDocuments(c.slug, documents, volumeFiles);
      const processedNames = new Set(docs.map((d) => d.filename));
      const pending = files.filter((f) => !processedNames.has(f.name)).length;
      const inReview = docs.filter((d) => d.status === "review").length;
      const approved = docs.filter((d) => d.status === "approved").length;
      const total = files.length;
      const progressPct =
        total === 0 ? 0 : Math.round((approved / total) * 100);
      return {
        customer: c,
        total,
        pending,
        inReview,
        approved,
        progressPct,
      };
    });
  }, [documents, volumeFiles]);

  const portfolioTotal = stats.reduce((sum, s) => sum + s.total, 0);
  const portfolioApproved = stats.reduce((sum, s) => sum + s.approved, 0);
  const portfolioPending = stats.reduce((sum, s) => sum + s.pending, 0);
  const portfolioReview = stats.reduce((sum, s) => sum + s.inReview, 0);
  const portfolioValue = stats.reduce(
    (sum, s) => sum + s.customer.transaction_m,
    0
  );

  return (
    <div className="max-w-7xl mx-auto w-full space-y-10">
      {/* Portfolio hero */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 bg-surface-container-low p-10 rounded-xl relative overflow-hidden">
          <div className="absolute -right-20 -top-20 w-64 h-64 bg-secondary-container/30 rounded-full blur-3xl" />
          <div className="relative z-10 max-w-lg">
            <span className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary text-xs font-medium rounded-full mb-6 tracking-wide font-label">
              <Icon name="workspaces" size={14} />
              Bulk Purchase Annuity (BPA) · Customer Portfolio
            </span>
            <h2 className="font-headline text-4xl mb-4 leading-tight text-on-surface">
              Customer Portal
              <br />
              <span className="text-on-surface-variant italic font-light">
                {CUSTOMERS.length} live engagements
              </span>
            </h2>
            <p className="font-body text-on-surface-variant leading-relaxed">
              Select a customer to review their scheme documents, track
              extraction progress, and approve records for transfer to Royal
              London.
            </p>
          </div>
        </div>

        {/* Portfolio stats */}
        <div className="lg:col-span-5 grid grid-cols-2 gap-3 h-full">
          <div className="bg-surface-container-lowest p-5 rounded-xl flex flex-col justify-between shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
            <Icon name="payments" className="text-primary mb-3" size={22} />
            <div>
              <div className="font-headline text-2xl font-medium mb-1">
                GBP {portfolioValue.toFixed(0)}m
              </div>
              <div className="font-body text-xs text-on-surface-variant">
                Indicative transaction value
              </div>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-5 rounded-xl flex flex-col justify-between shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
            <Icon name="description" className="text-secondary mb-3" size={22} />
            <div>
              <div className="font-headline text-2xl font-medium mb-1">
                {portfolioTotal}
              </div>
              <div className="font-body text-xs text-on-surface-variant">
                Total documents
              </div>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-5 rounded-xl flex flex-col justify-between shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
            <Icon
              name="pending_actions"
              className="text-on-tertiary-container mb-3"
              size={22}
            />
            <div>
              <div className="font-headline text-2xl font-medium mb-1">
                {portfolioPending + portfolioReview}
              </div>
              <div className="font-body text-xs text-on-surface-variant">
                Awaiting action
              </div>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-5 rounded-xl flex flex-col justify-between shadow-[0_4px_24px_rgba(26,28,28,0.02)]">
            <Icon name="verified" className="text-primary mb-3" size={22} />
            <div>
              <div className="font-headline text-2xl font-medium mb-1">
                {portfolioApproved}
              </div>
              <div className="font-body text-xs text-on-surface-variant">
                Approved records
              </div>
            </div>
          </div>
        </div>
      </section>

      {error && (
        <div className="p-5 bg-error-container rounded-xl">
          <p className="font-body text-sm text-on-error-container">{error}</p>
        </div>
      )}

      {/* Customer tiles */}
      <section>
        <div className="flex items-end justify-between mb-5">
          <h3 className="font-headline text-2xl text-on-surface">Customers</h3>
          <button
            onClick={() => {
              fetchVolumeFiles();
              fetchDocuments();
            }}
            disabled={loading}
            className="text-xs font-label text-on-surface-variant hover:text-on-surface flex items-center gap-1.5 transition-colors"
          >
            <Icon name="refresh" size={14} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {stats.map((s) => (
            <CustomerCard
              key={s.customer.slug}
              stats={s}
              onOpen={() => navigate(`/customers/${s.customer.slug}`)}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

function CustomerCard({
  stats,
  onOpen,
}: {
  stats: CustomerStats;
  onOpen: () => void;
}) {
  const { customer: c, total, pending, inReview, approved, progressPct } = stats;
  const processed = total - pending;

  return (
    <button
      onClick={onOpen}
      className="group text-left bg-surface-container-lowest hover:bg-white transition-all duration-200 rounded-xl p-6 border border-surface-container-high/40 hover:border-primary/30 hover:-translate-y-1 hover:shadow-[0_12px_40px_-12px_rgba(69,3,80,0.15)] flex flex-col gap-5"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-11 h-11 rounded-lg bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
            <Icon name={c.sector_icon} size={22} />
          </div>
          <div className="min-w-0">
            <h4 className="font-headline text-base text-on-surface leading-tight mb-0.5 truncate">
              {c.display}
            </h4>
            <p className="font-body text-xs text-on-surface-variant truncate">
              {c.sector}
            </p>
          </div>
        </div>
        <Icon
          name="arrow_forward"
          size={18}
          className="text-on-surface-variant/40 group-hover:text-primary group-hover:translate-x-0.5 transition-all flex-shrink-0"
        />
      </div>

      {/* Progress */}
      <div>
        <div className="flex items-baseline justify-between mb-2">
          <span className="font-headline text-2xl text-on-surface">
            {processed}
            <span className="text-on-surface-variant/60 text-base font-normal"> / {total}</span>
          </span>
          <span className="font-label text-xs text-on-surface-variant uppercase tracking-wider">
            {progressPct}% approved
          </span>
        </div>
        <div className="h-1.5 bg-surface-container-high rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-primary-container transition-all"
            style={{ width: `${progressPct}%` }}
          />
        </div>
        <p className="font-body text-xs text-on-surface-variant mt-2">
          {processed} of {total} documents processed
        </p>
      </div>

      {/* Status strip */}
      <div className="grid grid-cols-3 gap-2">
        <StatPill
          icon="hourglass_empty"
          color="tertiary"
          value={pending}
          label="Pending"
        />
        <StatPill
          icon="fact_check"
          color="secondary"
          value={inReview}
          label="In Review"
        />
        <StatPill
          icon="verified"
          color="primary"
          value={approved}
          label="Approved"
        />
      </div>

      {/* Meta footer */}
      <div className="pt-4 border-t border-surface-container-high/60 flex items-center justify-between font-body text-xs text-on-surface-variant">
        <span className="flex items-center gap-1.5">
          <Icon name="savings" size={14} />
          {formatMoney(c.scheme_size_m)} scheme
        </span>
        <span className="flex items-center gap-1.5">
          <Icon name="group" size={14} />
          {formatMembers(c.member_count)}
        </span>
      </div>
    </button>
  );
}

function StatPill({
  icon,
  color,
  value,
  label,
}: {
  icon: string;
  color: "primary" | "secondary" | "tertiary";
  value: number;
  label: string;
}) {
  const colorClasses =
    color === "primary"
      ? "bg-primary/5 text-primary"
      : color === "secondary"
      ? "bg-secondary/5 text-secondary"
      : "bg-tertiary/5 text-tertiary";
  return (
    <div className={`rounded-lg px-3 py-2 ${colorClasses}`}>
      <div className="flex items-center gap-1.5 mb-0.5">
        <Icon name={icon} size={14} />
        <span className="font-headline text-sm font-medium">{value}</span>
      </div>
      <div className="font-label text-[10px] uppercase tracking-wider opacity-70">
        {label}
      </div>
    </div>
  );
}

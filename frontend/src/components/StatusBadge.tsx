import Icon from "./Icon";

const config: Record<string, { label: string; color: string; bg: string; icon: string; spin?: boolean }> = {
  uploaded: {
    label: "Uploaded",
    color: "text-surface-tint",
    bg: "bg-primary-fixed/20",
    icon: "schedule",
  },
  extracting: {
    label: "Extracting",
    color: "text-on-tertiary-container",
    bg: "bg-tertiary-fixed/30",
    icon: "sync",
    spin: true,
  },
  review: {
    label: "In Review",
    color: "text-on-tertiary-fixed-variant",
    bg: "bg-tertiary-fixed/50",
    icon: "rate_review",
  },
  approved: {
    label: "Approved",
    color: "text-secondary",
    bg: "bg-secondary/10",
    icon: "check_circle",
  },
  error: {
    label: "Error",
    color: "text-error",
    bg: "bg-error-container",
    icon: "error",
  },
};

export default function StatusBadge({ status }: { status: string }) {
  const c = config[status] || config.uploaded;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-xs font-medium font-label ${c.color} ${c.bg}`}>
      <Icon name={c.icon} className={c.spin ? "animate-spin" : ""} size={14} />
      {c.label}
    </span>
  );
}

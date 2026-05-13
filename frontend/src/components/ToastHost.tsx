import { Link } from "react-router-dom";
import Icon from "./Icon";
import { useToastStore } from "../stores/toastStore";

const TONE_STYLES: Record<string, { icon: string; iconClass: string }> = {
  success: { icon: "check_circle", iconClass: "text-primary" },
  info: { icon: "info", iconClass: "text-on-surface-variant" },
  error: { icon: "error", iconClass: "text-error" },
};

export default function ToastHost() {
  const toasts = useToastStore((s) => s.toasts);
  const dismiss = useToastStore((s) => s.dismiss);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => {
        const tone = TONE_STYLES[t.tone ?? "success"] ?? TONE_STYLES.success;
        return (
          <div
            key={t.id}
            className="pointer-events-auto bg-surface-container-lowest border border-outline-variant/30 rounded-xl px-4 py-3 shadow-[0_10px_40px_-10px_rgba(26,28,28,0.25)] min-w-[280px] max-w-sm flex items-start gap-3 animate-[fadeIn_0.2s_ease-out]"
          >
            <Icon name={tone.icon} size={20} className={`${tone.iconClass} flex-shrink-0 mt-0.5`} />
            <div className="flex-1 min-w-0">
              <div className="font-body font-medium text-sm text-on-surface truncate">
                {t.title}
              </div>
              {t.description && (
                <div className="font-body text-xs text-on-surface-variant mt-0.5">
                  {t.description}
                </div>
              )}
              {t.action && (
                <Link
                  to={t.action.to}
                  onClick={() => dismiss(t.id)}
                  className="inline-flex items-center gap-1 mt-1.5 text-primary font-label text-xs font-medium hover:underline"
                >
                  {t.action.label}
                  <Icon name="chevron_right" size={14} />
                </Link>
              )}
            </div>
            <button
              onClick={() => dismiss(t.id)}
              className="flex-shrink-0 text-on-surface-variant/60 hover:text-on-surface transition-colors"
              aria-label="Dismiss notification"
            >
              <Icon name="close" size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
}

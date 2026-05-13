import { useState } from "react";
import Icon from "./Icon";
import type { ExtractedField } from "../stores/documentStore";

const confidenceConfig: Record<string, { dot: string; border: string; label: string }> = {
  high:   { dot: "bg-secondary",        border: "border-secondary/20 hover:border-secondary/50", label: "High" },
  medium: { dot: "bg-tertiary-fixed-dim", border: "border-tertiary-fixed hover:border-tertiary-fixed-dim", label: "Med" },
  low:    { dot: "bg-error",             border: "border-error/20 hover:border-error/50", label: "Low" },
};

interface Props {
  field: ExtractedField;
  onUpdate: (fieldId: number, update: { reviewed_value?: string; is_approved?: boolean }) => void;
}

export default function FieldEditor({ field, onUpdate }: Props) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(field.reviewed_value ?? field.extracted_value ?? "");

  const displayValue = field.reviewed_value ?? field.extracted_value ?? "N/A";
  const conf = confidenceConfig[field.confidence] || confidenceConfig.medium;

  const handleSave = () => { onUpdate(field.id, { reviewed_value: value }); setEditing(false); };
  const handleCancel = () => { setValue(field.reviewed_value ?? field.extracted_value ?? ""); setEditing(false); };

  return (
    <div className={`group relative p-4 rounded-xl border-l-4 ${conf.border} transition-colors ${
      field.is_approved
        ? "bg-surface-container-lowest shadow-none"
        : "bg-surface-container-lowest shadow-[0_4px_20px_-5px_rgba(0,0,0,0.05)]"
    }`}>
      <div className="flex justify-between items-start mb-2">
        <label className="font-label text-xs font-semibold text-on-surface-variant uppercase tracking-wider">{field.field_name}</label>
        <div className={`${field.confidence === "high" ? "bg-secondary-container/50 text-on-secondary-container" : field.confidence === "low" ? "bg-error-container/50 text-on-error-container" : "bg-tertiary-fixed/30 text-on-tertiary-fixed-variant"} text-xs px-2 py-0.5 rounded-sm flex items-center gap-1 font-medium`}>
          <Icon name={field.confidence === "high" ? "check_circle" : field.confidence === "low" ? "error" : "help"} size={14} />
          {conf.label}
        </div>
      </div>

      {editing ? (
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className="flex-1 bg-surface-container-high border-none border-b-2 border-transparent focus:bg-surface-container-lowest focus:border-secondary rounded px-3 py-2 text-sm text-on-surface font-body transition-all focus:ring-0"
            autoFocus
            onKeyDown={(e) => { if (e.key === "Enter") handleSave(); if (e.key === "Escape") handleCancel(); }}
          />
          <button onClick={handleSave} className="text-xs text-secondary hover:text-secondary/80 font-medium transition-colors flex items-center gap-1 font-label">
            <Icon name="done" size={16} /> Save
          </button>
          <button onClick={handleCancel} className="text-xs text-on-surface-variant hover:text-primary transition-colors font-label">
            Cancel
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-3">
          <div className="flex-1 bg-surface px-3 py-2 rounded font-body text-sm text-on-surface border-b-2 border-transparent">
            {displayValue}
          </div>
          <div className={`w-2 h-2 rounded-full ${conf.dot} flex-shrink-0`} title={`${conf.label} Confidence`} />
        </div>
      )}

      {/* Action buttons on hover */}
      {!editing && (
        <div className="flex justify-end gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onClick={() => setEditing(true)} className="text-xs text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 font-label">
            <Icon name="edit" size={16} /> Edit
          </button>
          {!field.is_approved && (
            <button onClick={() => onUpdate(field.id, { is_approved: true })} className="text-xs text-secondary hover:text-secondary/80 font-medium transition-colors flex items-center gap-1 font-label">
              <Icon name="done" size={16} /> Approve
            </button>
          )}
        </div>
      )}
    </div>
  );
}

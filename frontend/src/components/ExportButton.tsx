import Icon from "./Icon";

interface Props {
  format: "csv" | "json";
}

export default function ExportButton({ format }: Props) {
  return (
    <button
      onClick={() => window.open(`/api/export/${format}`, "_blank")}
      className="flex items-center gap-2 text-on-surface-variant font-label font-medium px-4 py-2 rounded-md bg-surface-container-lowest hover:bg-surface-container-low transition-colors shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)]"
    >
      <Icon name="download" size={16} />
      {format.toUpperCase()}
    </button>
  );
}

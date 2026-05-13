import { useCallback, useState } from "react";
import { Upload, FileText, Loader2 } from "lucide-react";

interface Props {
  onFileAccepted: (file: File) => void;
  loading?: boolean;
}

export default function FileDropzone({ onFileAccepted, loading }: Props) {
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) onFileAccepted(file);
    },
    [onFileAccepted]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFileAccepted(file);
    },
    [onFileAccepted]
  );

  return (
    <label
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      className={`
        relative flex flex-col items-center justify-center w-full h-48
        border-2 border-dashed rounded-xl cursor-pointer transition-all
        ${
          dragOver
            ? "border-rl-purple bg-rl-purple-50"
            : "border-gray-200 bg-white hover:border-rl-purple-200 hover:bg-gray-50"
        }
        ${loading ? "pointer-events-none opacity-60" : ""}
      `}
    >
      <input
        type="file"
        accept=".pdf,.xlsx,.xls"
        className="hidden"
        onChange={handleChange}
        disabled={loading}
      />
      {loading ? (
        <>
          <Loader2 size={32} className="text-rl-purple animate-spin mb-3" />
          <p className="text-sm text-gray-600">Processing...</p>
        </>
      ) : (
        <>
          <div className="w-12 h-12 bg-rl-purple-50 rounded-full flex items-center justify-center mb-3">
            <Upload size={22} className="text-rl-purple" />
          </div>
          <p className="text-sm font-medium text-gray-700 mb-1">
            Drop a file here, or click to browse
          </p>
          <div className="flex gap-2 mt-2">
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-gray-100 text-xs text-gray-600">
              <FileText size={12} /> PDF
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-gray-100 text-xs text-gray-600">
              <FileText size={12} /> XLSX
            </span>
          </div>
        </>
      )}
    </label>
  );
}

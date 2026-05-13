import { create } from "zustand";

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  upload_time: string;
  status: string;
  raw_text?: string;
  document_kind?: string | null;
}

export interface ExtractedField {
  id: number;
  document_id: number;
  field_name: string;
  field_category: string;
  extracted_value: string | null;
  reviewed_value: string | null;
  confidence: string;
  is_approved: boolean;
}

export interface VolumeFile {
  name: string;
  path: string;
  size: number | null;
  customer?: string;
  customer_display?: string;
  relative_path?: string;
}

interface DocumentStore {
  documents: Document[];
  currentDocument: Document | null;
  fields: ExtractedField[];
  volumeFiles: VolumeFile[];
  volumePath: string;
  loading: boolean;
  error: string | null;

  fetchDocuments: () => Promise<void>;
  fetchDocument: (id: number) => Promise<void>;
  fetchFields: (documentId: number) => Promise<void>;
  uploadFile: (file: File) => Promise<Document>;
  extractFields: (documentId: number) => Promise<void>;
  updateField: (
    fieldId: number,
    update: { reviewed_value?: string; is_approved?: boolean }
  ) => Promise<void>;
  approveAll: (documentId: number) => Promise<void>;
  bulkApproveDocuments: (documentIds: number[]) => Promise<number>;
  fetchVolumeFiles: () => Promise<void>;
  uploadFromVolume: (filename: string) => Promise<Document>;
}

export function getCustomerFiles(slug: string, volumeFiles: VolumeFile[]): VolumeFile[] {
  return volumeFiles.filter((f) => f.customer === slug);
}

export function getCustomerDocuments(
  slug: string,
  documents: Document[],
  volumeFiles: VolumeFile[]
): Document[] {
  const names = new Set(getCustomerFiles(slug, volumeFiles).map((f) => f.name));
  return documents.filter((d) => names.has(d.filename));
}

const api = async (url: string, options?: RequestInit) => {
  const res = await fetch(url, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    const err: any = new Error(body.detail || res.statusText);
    err.status = res.status;
    err.url = url;
    throw err;
  }
  return res.json();
};

export const useDocumentStore = create<DocumentStore>((set) => ({
  documents: [],
  currentDocument: null,
  fields: [],
  volumeFiles: [],
  volumePath: "",
  loading: false,
  error: null,

  fetchDocuments: async () => {
    set({ loading: true, error: null });
    try {
      const docs = await api("/api/documents");
      set({ documents: docs, loading: false });
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  fetchDocument: async (id) => {
    set({ loading: true, error: null });
    try {
      const doc = await api(`/api/documents/${id}`);
      set({ currentDocument: doc, loading: false });
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  fetchFields: async (documentId) => {
    set({ loading: true, error: null });
    try {
      const fields = await api(`/api/documents/${documentId}/fields`);
      set({ fields, loading: false });
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  uploadFile: async (file) => {
    set({ loading: true, error: null });
    const form = new FormData();
    form.append("file", file);
    try {
      const doc = await api("/api/upload", { method: "POST", body: form });
      set((s) => ({
        documents: [doc, ...s.documents],
        loading: false,
      }));
      return doc;
    } catch (e: any) {
      set({ error: e.message, loading: false });
      throw e;
    }
  },

  extractFields: async (documentId) => {
    set({ loading: true, error: null });
    try {
      const fields = await api(`/api/extract/${documentId}`, {
        method: "POST",
      });
      set({ fields, loading: false });

      set((s) => ({
        documents: s.documents.map((d) =>
          d.id === documentId ? { ...d, status: "review" } : d
        ),
        currentDocument: s.currentDocument
          ? { ...s.currentDocument, status: "review" }
          : null,
      }));
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  updateField: async (fieldId, update) => {
    try {
      const updated = await api(`/api/fields/${fieldId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(update),
      });
      set((s) => ({
        fields: s.fields.map((f) => (f.id === fieldId ? updated : f)),
      }));
    } catch (e: any) {
      set({ error: e.message });
    }
  },

  approveAll: async (documentId) => {
    set({ loading: true });
    try {
      await api(`/api/documents/${documentId}/approve-all`, {
        method: "POST",
      });
      set((s) => ({
        fields: s.fields.map((f) => ({ ...f, is_approved: true })),
        documents: s.documents.map((d) =>
          d.id === documentId ? { ...d, status: "approved" } : d
        ),
        currentDocument: s.currentDocument
          ? { ...s.currentDocument, status: "approved" }
          : null,
        loading: false,
      }));
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  bulkApproveDocuments: async (documentIds) => {
    if (documentIds.length === 0) return 0;
    set({ loading: true, error: null });
    try {
      const res = await api("/api/documents/bulk-approve-docs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_ids: documentIds }),
      });
      const idSet = new Set(documentIds);
      set((s) => ({
        documents: s.documents.map((d) =>
          idSet.has(d.id) ? { ...d, status: "approved" } : d
        ),
        fields: s.fields.map((f) =>
          idSet.has(f.document_id) ? { ...f, is_approved: true } : f
        ),
        currentDocument:
          s.currentDocument && idSet.has(s.currentDocument.id)
            ? { ...s.currentDocument, status: "approved" }
            : s.currentDocument,
        loading: false,
      }));
      return res?.approved ?? documentIds.length;
    } catch (e: any) {
      set({ error: e.message, loading: false });
      throw e;
    }
  },

  fetchVolumeFiles: async () => {
    set({ loading: true, error: null });
    try {
      const data = await api("/api/volume-files");
      set({
        volumeFiles: data.files,
        volumePath: data.volume_path,
        loading: false,
      });
    } catch (e: any) {
      set({ error: e.message, loading: false });
    }
  },

  uploadFromVolume: async (filename) => {
    set({ loading: true, error: null });
    try {
      const doc = await api(
        `/api/upload-from-volume?filename=${encodeURIComponent(filename)}`,
        { method: "POST" }
      );
      set((s) => ({
        documents: [doc, ...s.documents],
        loading: false,
      }));
      return doc;
    } catch (e: any) {
      set({ error: e.message, loading: false });
      throw e;
    }
  },
}));

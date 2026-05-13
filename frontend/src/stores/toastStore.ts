import { create } from "zustand";

export interface ToastAction {
  label: string;
  to: string;
}

export interface Toast {
  id: number;
  title: string;
  description?: string;
  action?: ToastAction;
  tone?: "success" | "info" | "error";
}

interface ToastStore {
  toasts: Toast[];
  push: (toast: Omit<Toast, "id">) => number;
  dismiss: (id: number) => void;
}

const AUTO_DISMISS_MS = 5000;

let nextId = 1;

export const useToastStore = create<ToastStore>((set, get) => ({
  toasts: [],

  push: (toast) => {
    const id = nextId++;
    set((s) => ({ toasts: [...s.toasts, { id, tone: "success", ...toast }] }));
    if (typeof window !== "undefined") {
      window.setTimeout(() => get().dismiss(id), AUTO_DISMISS_MS);
    }
    return id;
  },

  dismiss: (id) => {
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
  },
}));

// Convenience helper so non-React code (detached promises) can push toasts
// without needing to subscribe to the store.
export function pushToast(toast: Omit<Toast, "id">): number {
  return useToastStore.getState().push(toast);
}

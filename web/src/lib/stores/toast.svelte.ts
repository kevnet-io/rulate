/**
 * Toast notification store
 * Manages a queue of toast messages for user feedback
 */

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration: number;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (message: string, type?: ToastType, duration?: number) => void;
  removeToast: (id: string) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
  clear: () => void;
  getToasts: () => Toast[];
  remove: (id: string) => void;
}

function createToastStore(): ToastStore {
  let toasts = $state<Toast[]>([]);

  function addToast(
    message: string,
    type: ToastType = "info",
    duration: number = 5000,
  ) {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const toast: Toast = { id, message, type, duration };

    toasts = [...toasts, toast];

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }

  function removeToast(id: string) {
    toasts = toasts.filter((t) => t.id !== id);
  }

  function success(message: string, duration: number = 5000) {
    addToast(message, "success", duration);
  }

  function error(message: string, duration: number = 7000) {
    // Errors stay longer
    addToast(message, "error", duration);
  }

  function warning(message: string, duration: number = 6000) {
    addToast(message, "warning", duration);
  }

  function info(message: string, duration: number = 5000) {
    addToast(message, "info", duration);
  }

  function clear() {
    toasts = [];
  }

  function getToasts() {
    return toasts;
  }

  return {
    get toasts() {
      return toasts;
    },
    addToast,
    removeToast,
    remove: removeToast, // Alias for consistency
    success,
    error,
    warning,
    info,
    clear,
    getToasts,
  };
}

export const toastStore = createToastStore();

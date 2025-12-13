/**
 * Modal store
 * Manages modal state and provides confirmation dialogs
 */

interface ModalData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDanger?: boolean;
}

interface ModalState {
  isOpen: boolean;
  data: ModalData | null;
  resolve: ((value: boolean) => void) | null;
}

interface ModalStore {
  isOpen: boolean;
  data: ModalData | null;
  open: (data: ModalData) => void;
  close: () => void;
  confirm: (data: ModalData) => Promise<boolean>;
  handleConfirm: () => void;
  handleCancel: () => void;
}

function createModalStore(): ModalStore {
  let state = $state<ModalState>({
    isOpen: false,
    data: null,
    resolve: null,
  });

  function open(data: ModalData) {
    state = {
      isOpen: true,
      data,
      resolve: null,
    };
  }

  function close() {
    state = {
      isOpen: false,
      data: null,
      resolve: null,
    };
  }

  function confirm(data: ModalData): Promise<boolean> {
    return new Promise((resolve) => {
      state = {
        isOpen: true,
        data,
        resolve,
      };
    });
  }

  function handleConfirm() {
    if (state.resolve) {
      state.resolve(true);
    }
    close();
  }

  function handleCancel() {
    if (state.resolve) {
      state.resolve(false);
    }
    close();
  }

  return {
    get isOpen() {
      return state.isOpen;
    },
    get data() {
      return state.data;
    },
    open,
    close,
    confirm,
    handleConfirm,
    handleCancel,
  };
}

export const modalStore = createModalStore();

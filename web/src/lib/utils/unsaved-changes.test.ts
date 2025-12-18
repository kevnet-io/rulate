import { beforeEach, describe, expect, it, vi } from "vitest";

import { useUnsavedChangesWarning } from "./unsaved-changes.svelte";

type BeforeNavigateArgs = {
  cancel: () => void;
  to: unknown;
};

let onMountCleanup: (() => void) | undefined;
let beforeNavigateCallback:
  | ((args: BeforeNavigateArgs) => void | Promise<void>)
  | undefined;

vi.mock("svelte", () => ({
  onMount: (fn: () => void | (() => void)) => {
    const cleanup = fn();
    if (typeof cleanup === "function") onMountCleanup = cleanup;
  },
}));

vi.mock("$app/navigation", () => ({
  beforeNavigate: (fn: (args: BeforeNavigateArgs) => void | Promise<void>) => {
    beforeNavigateCallback = fn;
  },
}));

const confirmMock = vi.fn<(options: unknown) => Promise<boolean>>();
vi.mock("$lib/stores/modal.svelte", () => ({
  modalStore: {
    confirm: (options: unknown) => confirmMock(options),
  },
}));

describe("utils/unsaved-changes", () => {
  beforeEach(() => {
    confirmMock.mockReset();
    onMountCleanup = undefined;
    beforeNavigateCallback = undefined;
  });

  it("registers and unregisters beforeunload handler", () => {
    const addSpy = vi.spyOn(window, "addEventListener");
    const removeSpy = vi.spyOn(window, "removeEventListener");

    useUnsavedChangesWarning(() => false);

    expect(addSpy).toHaveBeenCalledWith("beforeunload", expect.any(Function));
    expect(onMountCleanup).toBeTypeOf("function");

    onMountCleanup?.();

    expect(removeSpy).toHaveBeenCalledWith(
      "beforeunload",
      expect.any(Function),
    );
  });

  it("sets beforeunload returnValue when changes exist", () => {
    let handler: ((e: BeforeUnloadEvent) => void) | undefined;
    vi.spyOn(window, "addEventListener").mockImplementation(((
      type: string,
      listener: EventListenerOrEventListenerObject,
    ) => {
      if (type === "beforeunload" && typeof listener === "function") {
        handler = listener as unknown as (e: BeforeUnloadEvent) => void;
      }
    }) as typeof window.addEventListener);

    useUnsavedChangesWarning(() => true);

    const e = {
      preventDefault: vi.fn(),
      returnValue: undefined as unknown,
    } as unknown as BeforeUnloadEvent;

    handler?.(e);

    expect(e.preventDefault).toHaveBeenCalled();
    expect(e.returnValue).toBe("");
  });

  it("does nothing on beforeunload when no changes exist", () => {
    let handler: ((e: BeforeUnloadEvent) => void) | undefined;
    vi.spyOn(window, "addEventListener").mockImplementation(((
      type: string,
      listener: EventListenerOrEventListenerObject,
    ) => {
      if (type === "beforeunload" && typeof listener === "function") {
        handler = listener as unknown as (e: BeforeUnloadEvent) => void;
      }
    }) as typeof window.addEventListener);

    useUnsavedChangesWarning(() => false);

    const e = {
      preventDefault: vi.fn(),
      returnValue: undefined as unknown,
    } as unknown as BeforeUnloadEvent;

    handler?.(e);

    expect(e.preventDefault).not.toHaveBeenCalled();
    expect(e.returnValue).toBeUndefined();
  });

  it("prompts on navigation when changes exist and cancels on decline", async () => {
    confirmMock.mockResolvedValueOnce(false);
    const cancel = vi.fn();

    useUnsavedChangesWarning(() => true);
    expect(beforeNavigateCallback).toBeTypeOf("function");

    await beforeNavigateCallback?.({ cancel, to: { pathname: "/next" } });

    expect(confirmMock).toHaveBeenCalled();
    expect(cancel).toHaveBeenCalled();
  });

  it("does not cancel navigation when user confirms", async () => {
    confirmMock.mockResolvedValueOnce(true);
    const cancel = vi.fn();

    useUnsavedChangesWarning(() => true);
    await beforeNavigateCallback?.({ cancel, to: { pathname: "/next" } });

    expect(confirmMock).toHaveBeenCalled();
    expect(cancel).not.toHaveBeenCalled();
  });

  it("does not prompt on navigation when no changes exist", async () => {
    const cancel = vi.fn();

    useUnsavedChangesWarning(() => false);
    await beforeNavigateCallback?.({ cancel, to: { pathname: "/next" } });

    expect(confirmMock).not.toHaveBeenCalled();
    expect(cancel).not.toHaveBeenCalled();
  });

  it("does not prompt on navigation when target is missing", async () => {
    const cancel = vi.fn();

    useUnsavedChangesWarning(() => true);
    await beforeNavigateCallback?.({ cancel, to: null });

    expect(confirmMock).not.toHaveBeenCalled();
    expect(cancel).not.toHaveBeenCalled();
  });
});

// @vitest-environment jsdom
import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import DocsPage from "./DocsPage";

const setEnd = vi.fn();
vi.mock("@/contexts/usePageHeader", () => ({ usePageHeader: () => ({ setEnd }) }));
vi.mock("@/i18n", () => ({ useI18n: () => ({ t: { app: { nav: { documentation: "Documentation" } } } }) }));
vi.mock("@/plugins", () => ({ PluginSlot: () => null }));

it("renders the bundled SCI manual without a remote frame or fetch", async () => {
  const fetchSpy = vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("offline"));
  const container = document.createElement("div");
  const root = createRoot(container);
  try {
    await act(async () => root.render(<DocsPage />));
    expect(container.textContent).toContain("Boltzmann Labs");
    expect(container.textContent).toContain("/Add_boltz");
    expect(container.querySelector("iframe")).toBeNull();
    expect(container.querySelector('a[href*="nousresearch"]')).toBeNull();
    expect(fetchSpy).not.toHaveBeenCalled();
  } finally {
    await act(async () => root.unmount());
    fetchSpy.mockRestore();
  }
});

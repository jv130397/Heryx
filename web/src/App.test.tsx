import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

vi.mock("./PedigreeScene", () => ({
  PedigreeScene: () => <div aria-label="Heredograma tridimensional interativo" />
}));

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation(() => ({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn()
  }))
});

afterEach(cleanup);

describe("RarePedigree Web welcome", () => {
  it("renders the 3D scene and core project actions", async () => {
    render(<App />);
    expect(await screen.findByLabelText("Heredograma tridimensional interativo")).toBeVisible();
    expect(screen.getByRole("button", { name: /Nova família/ })).toBeEnabled();
    expect(screen.getByRole("button", { name: /Abrir projeto/ })).toBeEnabled();
  });

  it("keeps recent projects visually separate from the primary actions", async () => {
    render(<App />);
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Projetos recentes" })).toBeVisible()
    );
    expect(screen.getByText("Família Silva")).toBeVisible();
  });
});

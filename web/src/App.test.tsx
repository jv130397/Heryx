import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

vi.mock("./PedigreeScene", () => ({
  PedigreeScene: () => <div aria-label="Observatório genômico tridimensional interativo" />
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
    expect(await screen.findByLabelText("Observatório genômico tridimensional interativo")).toBeVisible();
    expect(screen.getByRole("button", { name: /Entrar no laboratório/ })).toBeEnabled();
    expect(screen.getByRole("button", { name: /Continuar projeto/ })).toBeEnabled();
  });

  it("links the welcome experience to the public GitHub repository", async () => {
    render(<App />);
    await waitFor(() => expect(screen.getAllByRole("link", { name: /Ver no GitHub/ })).toHaveLength(2));
    for (const link of screen.getAllByRole("link", { name: /Ver no GitHub/ })) {
      expect(link).toHaveAttribute("href", "https://github.com/jv130397/RarePedigree-Studio");
    }
  });
});

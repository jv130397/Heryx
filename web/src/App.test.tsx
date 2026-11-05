import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
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

  it("lets the user skip the cinematic sequence", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Pular introdução/ }));
    expect(screen.queryByRole("button", { name: /Pular introdução/ })).not.toBeInTheDocument();
  });

  it("uses João Vitor as a contextual guide", async () => {
    render(<App />);
    fireEvent.mouseEnter(screen.getByRole("button", { name: /Continuar projeto/ }));
    await waitFor(() => expect(screen.getByText("Pronto para retomar seu projeto.")).toBeInTheDocument());
  });

  it("inspects a local RarePedigree project without uploading it", async () => {
    const { container } = render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Continuar projeto/ }));
    const input = container.querySelector<HTMLInputElement>('input[type="file"]');
    const project = new File([JSON.stringify({ schema_version: "0.4.0", title: "Família teste", individuals: [{ id: "1" }], relationships: [] })], "family.rps.json", { type: "application/json" });
    fireEvent.change(input!, { target: { files: [project] } });
    await waitFor(() => expect(screen.getByRole("heading", { name: "Família teste" })).toBeVisible());
    expect(screen.getByText("0.4.0")).toBeVisible();
    expect(screen.getByRole("button", { name: /Abrir visualização no editor/ })).toBeEnabled();
  });

  it("creates a new project through the guided mission", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Entrar no laboratório/ }));
    await waitFor(() => expect(screen.getByRole("dialog", { name: /Inicie uma história familiar/ })).toBeVisible());
    fireEvent.change(screen.getByLabelText("Nome do projeto"), { target: { value: "Família Aurora" } });
    fireEvent.click(screen.getByRole("button", { name: /^Continuar$/ }));
    await waitFor(() => expect(screen.getByRole("button", { name: /Feminino/ })).toBeVisible());
    fireEvent.click(screen.getByRole("button", { name: /Feminino/ }));
    fireEvent.click(screen.getByLabelText(/Apresenta o fenótipo/));
    fireEvent.click(screen.getByRole("button", { name: /^Continuar$/ }));
    await waitFor(() => expect(screen.getByText("Família Aurora")).toBeVisible());
    fireEvent.click(screen.getByRole("button", { name: /Criar heredograma/ }));
    await waitFor(() => expect(screen.getByLabelText("Editor de heredograma")).toBeVisible(), { timeout: 2500 });
    expect(screen.getByRole("img", { name: /Heredograma carregado: Família Aurora/ })).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Selecionar indivíduo I-1" }));
    await waitFor(() => expect(screen.getByRole("button", { name: /Filho/ })).toBeVisible());
    fireEvent.click(screen.getByRole("button", { name: /Filho/ }));
    expect(screen.getByText("P-2")).toBeVisible();
    expect(screen.getByRole("button", { name: "Selecionar indivíduo P-3" })).toHaveClass("newly-added");
    fireEvent.click(screen.getByRole("button", { name: "Desfazer" }));
    await waitFor(() => expect(screen.queryByText("P-2")).not.toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Refazer" }));
    await waitFor(() => expect(screen.getByText("P-2")).toBeVisible());
    fireEvent.click(screen.getByRole("button", { name: "Aumentar zoom" }));
    expect(screen.getByLabelText("Nível de zoom")).toHaveTextContent("110%");
    fireEvent.click(screen.getByRole("button", { name: "Ajustar à tela" }));
    expect(screen.getByLabelText("Nível de zoom")).toHaveTextContent("100%");
  });
});

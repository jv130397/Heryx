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

describe("Heryx Web welcome", () => {
  it("renders the professional clinical cover and core project actions", async () => {
    render(<App />);
    expect((await screen.findAllByLabelText(/Heryx — Hereditary Analytics/))[0]).toBeVisible();
    expect(screen.getAllByRole("button", { name: /Iniciar análise/ })[0]).toBeEnabled();
    expect(screen.getByRole("button", { name: /Carregar projeto/ })).toBeEnabled();
    expect(screen.getAllByRole("link", { name: /GitHub/ })[0]).toHaveAttribute("href", "https://github.com/jv130397/Heryx");
  });

  it("keeps the welcome chrome focused on brand and repository", async () => {
    render(<App />);
    expect(await screen.findByRole("link", { name: /Heryx/ })).toBeVisible();
    expect(screen.getByRole("link", { name: /GitHub/ })).toBeVisible();
  });

  it("builds the clinical scene with native vector elements", () => {
    render(<App />);
    expect(screen.getByRole("img", { name: /Heredograma clínico vetorial/ })).toBeInTheDocument();
    expect(document.querySelector(".clinical-cover__media")).not.toBeInTheDocument();
    expect(document.querySelector(".joao-in-lab")).not.toBeInTheDocument();
  });

  it("identifies the platform as hereditary analytics", async () => {
    render(<App />);
    expect(await screen.findByText(/HEREDITARY ANALYTICS/)).toBeInTheDocument();
  });

  it("inspects a local RarePedigree project without uploading it", async () => {
    const { container } = render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Carregar projeto/ }));
    const input = container.querySelector<HTMLInputElement>('input[type="file"]');
    const project = new File([JSON.stringify({ schema_version: "0.4.0", title: "Família teste", individuals: [{ id: "1" }], relationships: [] })], "family.rps.json", { type: "application/json" });
    fireEvent.change(input!, { target: { files: [project] } });
    await waitFor(() => expect(screen.getByRole("heading", { name: "Família teste" })).toBeVisible());
    expect(screen.getByText("0.4.0")).toBeVisible();
    expect(screen.getByRole("button", { name: /Abrir visualização no editor/ })).toBeEnabled();
  });

  it("creates a new project through the guided mission", async () => {
    const { container } = render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: /Iniciar análise/ })[0]);
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
    fireEvent.keyDown(window,{key:"+",ctrlKey:true});
    expect(screen.getByLabelText("Nível de zoom")).toHaveTextContent("110%");
    fireEvent.keyDown(window,{key:"0",ctrlKey:true});
    expect(screen.getByLabelText("Nível de zoom")).toHaveTextContent("100%");
    fireEvent.click(screen.getByRole("button",{name:"Selecionar indivíduo P-3"}));
    fireEvent.click(screen.getByLabelText("Probando"));
    fireEvent.click(screen.getByRole("button",{name:/Aplicar alterações/}));
    expect(container.querySelectorAll(".proband-arrow")).toHaveLength(1);
    fireEvent.click(screen.getByRole("button",{name:"Selecionar indivíduo P-3"}));
    fireEvent.keyDown(window,{key:"Escape"});
    await waitFor(()=>expect(screen.queryByRole("dialog",{name:/Editar indivíduo/})).not.toBeInTheDocument());
  });
});

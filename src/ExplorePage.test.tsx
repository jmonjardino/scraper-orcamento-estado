import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ExplorePage } from "./ExplorePage";
import { publicationFixture } from "./test/fixtures";

afterEach(() => vi.unstubAllGlobals());
function readyFixture() { return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(publicationFixture()) } as Response); }

describe("ExplorePage", () => {
  it("mostra árvore, ficha com caminho e fonte", async () => {
    vi.stubGlobal("fetch", vi.fn(readyFixture));
    render(<ExplorePage />);
    expect(await screen.findByRole("list", { name: "Árvore orçamental por programas" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /P-001 — Saúde/ }));
    expect(screen.getByRole("heading", { name: "Saúde" })).toBeInTheDocument();
    expect(screen.getAllByText("Total da Administração Central")).toHaveLength(2);
    expect(screen.getByRole("link", { name: /Ver fonte oficial.*Registo/ })).toHaveAttribute("href", "https://dados.gov.pt/mapa.xml");
  });
  it("pesquisa por código e declara que não mistura vistas", async () => {
    vi.stubGlobal("fetch", vi.fn(readyFixture));
    render(<ExplorePage />);
    const input = await screen.findByRole("searchbox", { name: "Procurar por código ou designação oficial" });
    fireEvent.change(input, { target: { value: "p-001" } });
    expect((await screen.findAllByRole("button", { name: /P-001 — Saúde/ })).length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/Não existem filtros adicionais nesta vista/)).toBeInTheDocument();
  });

  it("expande e colapsa ramos com um botão nativo", async () => {
    vi.stubGlobal("fetch", vi.fn(readyFixture));
    render(<ExplorePage />);
    await screen.findByRole("list", { name: "Árvore orçamental por programas" });
    fireEvent.click(screen.getByRole("button", { name: "Colapsar Total da Administração Central" }));
    expect(screen.queryByRole("button", { name: /P-001 — Saúde/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Expandir Total da Administração Central" }));
    expect(screen.getByRole("button", { name: /P-001 — Saúde/ })).toBeInTheDocument();
  });
});

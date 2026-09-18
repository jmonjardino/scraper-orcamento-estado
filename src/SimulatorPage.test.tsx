import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Simulator, SimulatorPage } from "./SimulatorPage";
import { publicationFixture } from "./test/fixtures";

function response(body: unknown, ok = true, status = 200) {
  return Promise.resolve({ ok, status, json: () => Promise.resolve(body) } as Response);
}

afterEach(() => vi.unstubAllGlobals());

describe("SimulatorPage", () => {
  it("mantém o aviso responsável durante loading, erro, bloqueio e cenário pronto", async () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => undefined)));
    const loading = render(<SimulatorPage />);
    expect(screen.getByRole("heading", { name: "Este é um cenário de montantes" })).toBeInTheDocument();
    expect(screen.getByText("A carregar dados validados…")).toBeInTheDocument();
    loading.unmount();

    vi.stubGlobal("fetch", vi.fn(() => response({}, false, 404)));
    const error = render(<SimulatorPage />);
    expect(await screen.findByRole("heading", { name: "Os dados não estão disponíveis" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Este é um cenário de montantes" })).toBeInTheDocument();
    error.unmount();

    const blockedData = publicationFixture();
    blockedData.view.selectable = false;
    vi.stubGlobal("fetch", vi.fn(() => response(blockedData)));
    const blocked = render(<SimulatorPage />);
    expect(await screen.findByRole("heading", { name: "Simulador indisponível para esta vista" })).toBeInTheDocument();
    expect(screen.getByText(/Esta vista ainda não está autorizada para criar cenários/)).toBeInTheDocument();
    expect(screen.queryByText(/selectable: false/)).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Este é um cenário de montantes" })).toBeInTheDocument();
    blocked.unmount();

    vi.stubGlobal("fetch", vi.fn(() => response(publicationFixture())));
    render(<SimulatorPage />);
    expect(await screen.findByRole("heading", { name: "Rubricas do cenário" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Este é um cenário de montantes" })).toBeInTheDocument();
  });

  it("mostra âmbito e restrições antes dos controlos sem misturar perspetivas", async () => {
    vi.stubGlobal("fetch", vi.fn(() => response(publicationFixture())));
    render(<SimulatorPage />);
    const context = await screen.findByRole("heading", { name: "O que está a ser simulado" });
    expect(context.compareDocumentPosition(screen.getByRole("checkbox", { name: "Excluir Total da Administração Central" })) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.getAllByText("Despesa condicionada por compromissos legais")).toHaveLength(2);
    expect(screen.getByText(/Não mistura classificações funcional/)).toBeInTheDocument();
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
  });

  it("explica que ausência de etiquetas não torna rubricas elimináveis", () => {
    const data = publicationFixture();
    data.nodes.forEach((node) => { node.factual_tags = []; });
    render(<Simulator data={data} />);
    expect(screen.getByText(/Esta ausência não significa que uma rubrica seja eliminável/)).toBeInTheDocument();
  });

  it("seleciona folhas, marca o pai parcial e reconcilia o painel", async () => {
    vi.stubGlobal("fetch", vi.fn(() => response(publicationFixture())));
    render(<SimulatorPage />);
    await screen.findByRole("heading", { name: "Rubricas do cenário" });
    fireEvent.click(screen.getByRole("button", { name: "Expandir Saúde" }));
    fireEvent.click(screen.getByRole("checkbox", { name: "Excluir Cuidados de saúde primários" }));
    expect(screen.getByRole("checkbox", { name: "Excluir Saúde" })).toBePartiallyChecked();
    const results = screen.getByRole("complementary", { name: "Resumo" });
    expect(within(results).getByText("1", { selector: "dd" })).toBeInTheDocument();
    expect(within(results).getByText(/8.*€.*\+.*2.*€.*=.*10.*€/)).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("1 rubricas terminais afetadas");
  });

  it("não referencia no estado colapsado um ramo ausente do DOM", async () => {
    vi.stubGlobal("fetch", vi.fn(() => response(publicationFixture())));
    render(<SimulatorPage />);
    const toggle = await screen.findByRole("button", { name: "Expandir Saúde" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(toggle).not.toHaveAttribute("aria-controls");
  });

  it("exclui um pai sem dupla contagem e permite reset acessível", async () => {
    vi.stubGlobal("fetch", vi.fn(() => response(publicationFixture())));
    render(<SimulatorPage />);
    await screen.findByRole("heading", { name: "Rubricas do cenário" });
    const reset = screen.getByRole("button", { name: "Repor cenário" });
    expect(reset).toBeDisabled();
    fireEvent.click(screen.getByRole("checkbox", { name: "Excluir Saúde" }));
    expect(screen.getByRole("checkbox", { name: "Excluir Saúde" })).toBeChecked();
    expect(screen.getByText("2", { selector: "dd" })).toBeInTheDocument();
    expect(reset).toBeEnabled();
    fireEvent.click(reset);
    expect(screen.getByRole("checkbox", { name: "Excluir Saúde" })).not.toBeChecked();
    expect(reset).toBeDisabled();
    expect(screen.getByRole("status")).toHaveTextContent("Cenário reposto");
  });

  it("bloqueia uma árvore que não reconcilia e não mostra ações", async () => {
    const data = publicationFixture();
    data.nodes.find((node) => node.node_id.endsWith("acao-1"))!.amount_cents = 201;
    vi.stubGlobal("fetch", vi.fn(() => response(data)));
    render(<SimulatorPage />);
    expect(await screen.findByRole("heading", { name: "Simulador bloqueado por integridade" })).toBeInTheDocument();
    expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
    expect(screen.getByText(/não coincide com o total da raiz/)).toBeInTheDocument();
  });

  it("anuncia e limpa seleção quando muda o contexto", async () => {
    const first = publicationFixture();
    const { rerender } = render(<Simulator data={first} />);
    fireEvent.click(screen.getByRole("checkbox", { name: "Excluir Educação" }));
    expect(screen.getByRole("button", { name: "Repor cenário" })).toBeEnabled();
    const next = publicationFixture();
    next.dataset_sha256 = "b".repeat(64);
    rerender(<Simulator data={next} />);
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("O contexto dos dados mudou"));
    expect(screen.getByRole("checkbox", { name: "Excluir Educação" })).not.toBeChecked();
    expect(screen.getByRole("button", { name: "Repor cenário" })).toBeDisabled();
  });

  it("explica erro e tenta carregar novamente", async () => {
    const fetchMock = vi.fn()
      .mockImplementationOnce(() => response({}, false, 503))
      .mockImplementationOnce(() => response(publicationFixture()));
    vi.stubGlobal("fetch", fetchMock);
    render(<SimulatorPage />);
    expect(await screen.findByRole("heading", { name: "Os dados não estão disponíveis" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));
    expect(await screen.findByRole("heading", { name: "Rubricas do cenário" })).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});

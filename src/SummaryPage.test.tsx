import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DATA_URL } from "./data";
import { SummaryPage } from "./SummaryPage";
import { publicationFixture } from "./test/fixtures";

function response(body: unknown, ok = true, status = 200) {
  return Promise.resolve({ ok, status, json: () => Promise.resolve(body) } as Response);
}

afterEach(() => vi.unstubAllGlobals());

describe("SummaryPage", () => {
  it("mostra loading e só pede o pacote publicado local", () => {
    const fetchMock = vi.fn(() => new Promise<Response>(() => undefined));
    vi.stubGlobal("fetch", fetchMock);
    render(<SummaryPage />);
    expect(screen.getByText("A carregar dados validados…")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(DATA_URL, expect.any(Object));
    expect(DATA_URL).toBe("/data/current.json");
  });

  it("apresenta total, âmbito e uma fonte em cada cartão", async () => {
    vi.stubGlobal("fetch", vi.fn(() => response(publicationFixture())));
    render(<SummaryPage />);
    expect(await screen.findByRole("heading", { name: /10.*€/ })).toBeInTheDocument();
    expect(screen.getByText(/Administração Central, não consolidada/)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Saúde" })).toBeInTheDocument();
    expect(screen.getByText("60,0% do total")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /Ver fonte oficial/ })).toHaveLength(3);
  });

  it("explica a falha, move o foco e permite tentar novamente", async () => {
    const fetchMock = vi.fn()
      .mockImplementationOnce(() => response({}, false, 503))
      .mockImplementationOnce(() => response(publicationFixture()));
    vi.stubGlobal("fetch", fetchMock);
    render(<SummaryPage />);
    const errorHeading = await screen.findByRole("heading", { name: "Os dados não estão disponíveis" });
    await waitFor(() => expect(errorHeading).toHaveFocus());
    fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));
    expect(await screen.findByRole("heading", { name: "Saúde" })).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("distingue um pacote vazio de um erro", async () => {
    const empty = publicationFixture();
    empty.nodes = empty.nodes.slice(0, 1);
    vi.stubGlobal("fetch", vi.fn(() => response(empty)));
    render(<SummaryPage />);
    expect(await screen.findByRole("heading", { name: "Não há áreas para apresentar" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Tentar novamente" })).not.toBeInTheDocument();
  });
});

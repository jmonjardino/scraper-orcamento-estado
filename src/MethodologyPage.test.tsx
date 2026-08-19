import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { MethodologyPage } from "./MethodologyPage";
import { publicationFixture } from "./test/fixtures";

afterEach(() => vi.unstubAllGlobals());

describe("MethodologyPage", () => {
  it("explica o processo e lista apenas fontes do pacote publicado", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve(publicationFixture()),
    } as Response)));
    render(<MethodologyPage />);
    expect(screen.getByRole("heading", { name: "Do documento à página" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Mapa XML" })).toBeInTheDocument();
    expect(screen.getByText(/Versão dos dados/)).toBeInTheDocument();
  });
});

import { describe, expect, it } from "vitest";
import { formatEuros, formatEurosExact } from "./format";

describe("format money", () => {
  it("preserva o último cêntimo no limite inteiro seguro", () => {
    const formatted = formatEurosExact(Number.MAX_SAFE_INTEGER);
    expect(formatted).toContain(",91");
    expect(formatted).toContain("€");
    expect(formatted.replace(/\D/g, "")).toBe(String(Number.MAX_SAFE_INTEGER));
  });

  it("arredonda a apresentação sem cêntimos usando aritmética inteira", () => {
    expect(formatEuros(149)).toMatch(/1.*€/);
    expect(formatEuros(150)).toMatch(/2.*€/);
  });

  it("rejeita montantes fora do contrato inteiro não negativo", () => {
    expect(() => formatEurosExact(Number.MAX_SAFE_INTEGER + 1)).toThrow(RangeError);
    expect(() => formatEurosExact(-1)).toThrow(RangeError);
  });
});

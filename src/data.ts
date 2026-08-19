import type { PublicationData } from "./types";

export const DATA_URL = `${import.meta.env.BASE_URL}data/current.json`;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

export function parsePublicationData(value: unknown): PublicationData {
  if (!isRecord(value) || !isRecord(value.release) || !isRecord(value.view)) {
    throw new Error("O pacote publicado não tem a estrutura esperada.");
  }
  if (!Array.isArray(value.nodes) || !Array.isArray(value.sources)) {
    throw new Error("O pacote publicado não contém nós e fontes válidos.");
  }
  if (typeof value.dataset_sha256 !== "string" || value.dataset_sha256.length !== 64) {
    throw new Error("O pacote publicado não identifica a versão dos dados.");
  }
  if (typeof value.release.year !== "number" || typeof value.view.root_node_id !== "string") {
    throw new Error("O pacote publicado não declara o ano ou o total de referência.");
  }
  return value as unknown as PublicationData;
}

export async function loadPublicationData(signal?: AbortSignal): Promise<PublicationData> {
  const response = await fetch(DATA_URL, {
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`Não foi possível carregar os dados publicados (HTTP ${response.status}).`);
  }
  return parsePublicationData(await response.json());
}

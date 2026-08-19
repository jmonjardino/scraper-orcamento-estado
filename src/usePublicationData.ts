import { useEffect, useState } from "react";
import { loadPublicationData } from "./data";
import type { PublicationData } from "./types";

type DataState =
  | { status: "loading"; data: null; error: null }
  | { status: "error"; data: null; error: string }
  | { status: "ready"; data: PublicationData; error: null };

export function usePublicationData() {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<DataState>({ status: "loading", data: null, error: null });

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading", data: null, error: null });
    loadPublicationData(controller.signal).then(
      (data) => setState({ status: "ready", data, error: null }),
      (error: unknown) => {
        if (!controller.signal.aborted) {
          setState({
            status: "error",
            data: null,
            error: error instanceof Error ? error.message : "Ocorreu um erro inesperado.",
          });
        }
      },
    );
    return () => controller.abort();
  }, [attempt]);

  return { ...state, retry: () => setAttempt((value) => value + 1) };
}

import { useEffect, useRef } from "react";

export function LoadingState() {
  return (
    <section className="state-card" aria-live="polite" aria-busy="true">
      <span className="spinner" aria-hidden="true" />
      <div>
        <h2>A carregar dados validados…</h2>
        <p>Estamos a obter o pacote publicado localmente.</p>
      </div>
    </section>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => heading.current?.focus(), []);
  return (
    <section className="state-card state-error" role="alert">
      <span className="state-icon" aria-hidden="true">!</span>
      <div>
        <h2 ref={heading} tabIndex={-1}>Os dados não estão disponíveis</h2>
        <p>{message}</p>
        <p>Nenhum número é mostrado sem passar pelo gate de publicação.</p>
        <button type="button" onClick={onRetry}>Tentar novamente</button>
      </div>
    </section>
  );
}

export function EmptyState() {
  return (
    <section className="state-card state-empty" role="status">
      <span className="state-icon" aria-hidden="true">0</span>
      <div>
        <h2>Não há áreas para apresentar</h2>
        <p>O pacote foi carregado, mas não contém áreas filhas do total de referência.</p>
      </div>
    </section>
  );
}

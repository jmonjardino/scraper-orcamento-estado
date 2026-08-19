import { EmptyState, ErrorState, LoadingState } from "./components/DataStates";
import { Shell } from "./components/Shell";
import { SourceLink } from "./components/SourceLink";
import { formatEuros, formatPercentage } from "./format";
import type { BudgetNode, PublishedSource } from "./types";
import { usePublicationData } from "./usePublicationData";

function AreaCard({ node, total, source }: { node: BudgetNode; total: number; source: PublishedSource }) {
  const ratio = total === 0 ? 0 : node.amount_cents / total;
  return (
    <article className="area-card">
      <div className="card-topline">
        <span className="official-code">{node.official_code}</span>
        <span className="percentage">{formatPercentage(node.amount_cents, total)} do total</span>
      </div>
      <h3>{node.official_label}</h3>
      <p className="area-value">{formatEuros(node.amount_cents)}</p>
      <div className="share-track" aria-hidden="true">
        <span style={{ width: `${Math.max(1, ratio * 100)}%` }} />
      </div>
      <SourceLink source={source} locator={node.source.locator} />
    </article>
  );
}

export function SummaryPage() {
  const state = usePublicationData();
  const data = state.status === "ready" ? state.data : undefined;
  const root = data?.nodes.find((node) => node.node_id === data.view.root_node_id);
  const areas = data?.nodes
    .filter((node) => node.parent_node_id === data.view.root_node_id)
    .sort((left, right) => left.sort_order - right.sort_order) ?? [];
  const sources = new Map(data?.sources.map((source) => [source.source_id, source]));

  return (
    <Shell
      currentPage="summary"
      data={data}
      title="Para onde vai a despesa orçamentada?"
      intro={
        <p>
          Um resumo do orçamento aprovado, organizado por programas. O total só aparece quando o pacote validado e
          aprovado está disponível.
        </p>
      }
    >
      <div className="content-width page-content">
        {state.status === "loading" ? <LoadingState /> : null}
        {state.status === "error" ? <ErrorState message={state.error} onRetry={state.retry} /> : null}
        {state.status === "ready" && (!root || areas.length === 0) ? <EmptyState /> : null}
        {state.status === "ready" && data && root && areas.length > 0 ? (
          <>
            <section className="reference-panel" aria-labelledby="total-title">
              <div>
                <p className="section-label">Total de referência</p>
                <h2 id="total-title">{formatEuros(root.amount_cents)}</h2>
                <p>
                  Despesa orçamentada da Administração Central, não consolidada, no OE aprovado de {data.release.year}.
                  A Segurança Social não está incluída neste total enquanto subsistema autónomo.
                </p>
              </div>
              <dl className="scope-list">
                <div><dt>Fase</dt><dd>OE aprovado</dd></div>
                <div><dt>Ótica</dt><dd>Programas do Mapa 1</dd></div>
                <div><dt>Medida</dt><dd>Despesa prevista, não execução</dd></div>
              </dl>
              {sources.get(root.source.source_id) ? (
                <SourceLink source={sources.get(root.source.source_id)!} locator={root.source.locator} />
              ) : null}
            </section>

            <section aria-labelledby="areas-title">
              <div className="section-heading">
                <div>
                  <p className="section-label">Visão por programas</p>
                  <h2 id="areas-title">Grandes áreas do orçamento</h2>
                </div>
                <p>{areas.length} programas, apresentados pela ordem oficial.</p>
              </div>
              <div className="area-grid">
                {areas.map((node) => {
                  const source = sources.get(node.source.source_id);
                  return source ? <AreaCard key={node.node_id} node={node} total={root.amount_cents} source={source} /> : null;
                })}
              </div>
            </section>

            <aside className="notice" aria-labelledby="notice-title">
              <span className="notice-icon" aria-hidden="true">i</span>
              <div>
                <h2 id="notice-title">O que este total não significa</h2>
                <p>
                  Não é despesa já executada, não é um total consolidado e não permite concluir quanto seria possível
                  poupar. Consulte a metodologia antes de comparar ou interpretar os valores.
                </p>
                <a href="/metodologia/">Ler metodologia e limitações</a>
              </div>
            </aside>
          </>
        ) : null}
      </div>
    </Shell>
  );
}

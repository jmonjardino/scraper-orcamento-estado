import { ErrorState, LoadingState } from "./components/DataStates";
import { Shell } from "./components/Shell";
import { SourceLink } from "./components/SourceLink";
import { usePublicationData } from "./usePublicationData";

export function MethodologyPage() {
  const state = usePublicationData();
  const data = state.status === "ready" ? state.data : undefined;

  return (
    <Shell
      currentPage="methodology"
      data={data}
      title="Metodologia e fontes"
      intro={<p>Como transformamos documentos oficiais num resumo rastreável — e onde é preciso ter cautela.</p>}
    >
      <div className="content-width page-content methodology-layout">
        <nav className="contents" aria-label="Nesta página">
          <strong>Nesta página</strong>
          <a href="#ambito">Âmbito</a>
          <a href="#processo">Processo</a>
          <a href="#limitacoes">Limitações</a>
          <a href="#fontes">Fontes oficiais</a>
        </nav>
        <div className="prose">
          <section id="ambito" tabIndex={-1}>
            <p className="section-label">1. Âmbito</p>
            <h2>Que orçamento está aqui?</h2>
            <p>
              Esta versão apresenta despesa prevista no Orçamento do Estado aprovado. Organiza o total da Administração
              Central por programas, de acordo com o Mapa 1, sem consolidação.
            </p>
            <dl className="definition-list">
              <div><dt>“Aprovado”</dt><dd>É o orçamento autorizado por lei, não uma proposta nem a execução posterior.</dd></div>
              <div><dt>“Não consolidado”</dt><dd>Os fluxos entre entidades do mesmo universo ainda podem estar incluídos.</dd></div>
              <div><dt>“Por programas”</dt><dd>É uma forma de classificação. Não deve ser somada a outras óticas do mesmo orçamento.</dd></div>
            </dl>
          </section>

          <section id="processo" tabIndex={-1}>
            <p className="section-label">2. Processo</p>
            <h2>Do documento à página</h2>
            <ol className="process-list">
              <li><strong>Arquivar.</strong> Guardamos uma cópia exata dos ficheiros oficiais e o respetivo SHA-256.</li>
              <li><strong>Normalizar.</strong> Convertemos códigos, designações e euros para um modelo com cêntimos inteiros.</li>
              <li><strong>Validar.</strong> Testamos estrutura, proveniência e igualdade entre filhos, raiz e total oficial.</li>
              <li><strong>Aprovar.</strong> Só o SHA revisto e aprovado por uma pessoa pode ser empacotado para a web.</li>
            </ol>
            <p>O navegador descarrega apenas esse pacote local. Não consulta automaticamente os sites oficiais.</p>
          </section>

          <section id="limitacoes" tabIndex={-1}>
            <p className="section-label">3. Limitações</p>
            <h2>O que fica de fora</h2>
            <ul className="check-list">
              <li>Execução mensal ou anual e alterações posteriores ao orçamento inicial.</li>
              <li>Receitas, impacto no défice, dívida, impostos ou uma estimativa de “poupança”.</li>
              <li>Regiões e autarquias; a Segurança Social não integra o total mostrado como subsistema autónomo.</li>
              <li>Comparação entre anos ou soma entre classificações programática, económica, funcional e orgânica.</li>
            </ul>
          </section>

          <section id="fontes" tabIndex={-1}>
            <p className="section-label">4. Fontes</p>
            <h2>Documentos oficiais utilizados</h2>
            {state.status === "loading" ? <LoadingState /> : null}
            {state.status === "error" ? <ErrorState message={state.error} onRetry={state.retry} /> : null}
            {state.status === "ready" && data && data.sources.length === 0 ? (
              <p className="inline-empty" role="status">O pacote publicado não declara fontes.</p>
            ) : null}
            {state.status === "ready" && data && data.sources.length > 0 ? (
              <div className="source-list">
                {data.sources.map((source) => (
                  <article key={source.source_id}>
                    <p className="source-publisher">{source.publisher}</p>
                    <h3>{source.title}</h3>
                    <p>{source.coverage}</p>
                    <SourceLink source={source} />
                  </article>
                ))}
              </div>
            ) : null}
            {data ? <p className="version">Versão dos dados: <code>{data.dataset_sha256}</code></p> : null}
          </section>
        </div>
      </div>
    </Shell>
  );
}

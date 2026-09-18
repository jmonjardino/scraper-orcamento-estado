import type { PropsWithChildren, ReactNode } from "react";
import type { PublicationData } from "../types";

interface ShellProps extends PropsWithChildren {
  currentPage: "summary" | "explore" | "simulate" | "methodology";
  data?: PublicationData;
  title: string;
  intro: ReactNode;
}

function phaseLabel(phase: string) {
  return phase === "approved_initial" ? "OE aprovado" : phase;
}

export function Shell({ currentPage, data, title, intro, children }: ShellProps) {
  const context = data
    ? [
        String(data.release.year),
        phaseLabel(data.release.phase),
        "Administração Central",
        "despesa orçamentada",
        "ótica por programas, não consolidada",
      ]
    : ["Contexto disponível quando os dados publicados carregarem"];

  return (
    <>
      <a className="skip-link" href="#conteudo-principal">
        Saltar para o conteúdo principal
      </a>
      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="/" aria-label="Explorador do Orçamento do Estado — página inicial">
            <span className="brand-mark" aria-hidden="true">OE</span>
            <span>Explorador do Orçamento do Estado</span>
          </a>
          <nav aria-label="Navegação principal">
            <a href="/" aria-current={currentPage === "summary" ? "page" : undefined}>Resumo</a>
            <a href="/explorar/" aria-current={currentPage === "explore" ? "page" : undefined}>Explorar</a>
            <a href="/simulador/" aria-current={currentPage === "simulate" ? "page" : undefined}>Simulador</a>
            <a href="/metodologia/" aria-current={currentPage === "methodology" ? "page" : undefined}>
              Metodologia e fontes
            </a>
          </nav>
        </div>
        <div className="context-bar" aria-label="Âmbito dos dados">
          <div className="header-inner context-list">
            {context.map((item) => <span key={item}>{item}</span>)}
          </div>
        </div>
        {data?.demo && (
          <div className="demo-banner" role="status">
            <div className="header-inner">{data.demo.notice}</div>
          </div>
        )}
      </header>
      <main id="conteudo-principal" tabIndex={-1}>
        <section className="page-heading">
          <div className="content-width">
            <p className="eyebrow">Orçamento explicado com âmbito e fonte</p>
            <h1>{title}</h1>
            <div className="lead">{intro}</div>
          </div>
        </section>
        {children}
      </main>
      <footer>
        <div className="content-width footer-inner">
          <p>Projeto independente baseado em fontes oficiais. Não substitui os documentos legais.</p>
          <a href="/metodologia/">Como os dados são preparados</a>
        </div>
      </footer>
    </>
  );
}

import type { PublishedSource } from "../types";

export function SourceLink({ source, locator }: { source: PublishedSource; locator?: string }) {
  return (
    <a className="source-link" href={source.url} rel="external">
      <span>Ver fonte oficial</span>
      <span aria-hidden="true">↗</span>
      {locator ? <span className="visually-hidden">, referência {locator}</span> : null}
    </a>
  );
}

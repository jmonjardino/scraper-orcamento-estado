# Evidência, dados e interface do OE 2026

Esta pasta documenta as decisões e resultados implementados desde a seleção das fontes até à fundação web. Os originais, o conjunto normalizado e os relatórios mantêm-se fora do bundle da interface; apenas o output aprovado do empacotador pode chegar a um build de release.

- [Fontes e protocolo de inspeção](fontes-e-inspecao.md)
- [Contrato de dados](contrato-de-dados.md)
- [Decisão da árvore](decisao-da-arvore.md)
- [Aquisição e arquivo](aquisicao-e-arquivo.md)
- [Normalização e árvore](normalizacao-e-arvore.md)
- [Qualidade e reconciliação](qualidade-e-reconciliacao.md)
- [Fundação web e gate de publicação](fundacao-web.md)
- [Validação da fundação web](validacao-fundacao-web.md)
- [Exploração detalhada](exploracao-detalhada.md)
- [Tokens visuais](tokens-visuais.md)

## Estado

`technically_validated_but_not_publishable`: o `Mapa1-2026.xml` oficial permite uma vista de programas da Administração Central não consolidada. As 20 folhas somam 352 472 389 960 €, exatamente o total de referência do Mapa 1, e o relatório técnico está em `validated`.

A publicação continua bloqueada: os termos de reutilização estão por resolver, a vista não está marcada como elegível e não existe aprovação humana vinculada ao SHA-256. A aplicação web está pronta para receber apenas o pacote que venha a passar esses gates; neste estado, o build de release falha de forma intencional.

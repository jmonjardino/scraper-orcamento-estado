# Parte 1 — Contrato de dados e fontes

## Documentos produzidos

- [Fontes e inspeção do OE 2026](../documentacao/oe2026/fontes-e-inspecao.md)
- [Contrato de dados](../documentacao/oe2026/contrato-de-dados.md)
- [Decisão da árvore](../documentacao/oe2026/decisao-da-arvore.md)
- [Tokens visuais](../documentacao/oe2026/tokens-visuais.md)

## Objetivo final

Definir inequivocamente o que significa “o Orçamento” no MVP antes de construir qualquer scraper ou base de dados.

## O que fazer

- Fixar o âmbito inicial: OE 2026 aprovado.
- Inventariar Lei, Mapas Contabilísticos, desenvolvimentos de orçamentação por programas e ficheiros de dados/XML da DGO.
- Inspecionar amostras reais dos formatos.
- Comparar as perspetivas programática, funcional, orgânica, económica e da Segurança Social.
- Escolher a árvore canónica — preferencialmente missão → programa → ação, se houver cobertura reconciliável.
- Definir universo, ótica contabilística, total de referência, unidade e arredondamento.
- Registar que perspetivas podem ser alternadas, mas não somadas entre si.

## Entregáveis

- Inventário de fontes.
- Dicionário de dados inicial.
- Contrato de dados com âmbito, total de referência e árvore canónica.
- Lista de lacunas e ambiguidades conhecidas.

## Estado da implementação

Os artefactos desta parte estão em [documentacao/oe2026](../documentacao/oe2026/README.md). O Mapa 1 XML oficial permite uma candidata tecnicamente reconciliada para Administração Central não consolidada por programa; ver [decisão da árvore](../documentacao/oe2026/decisao-da-arvore.md). A publicação permanece bloqueada enquanto faltarem termos de reutilização e revisão final dos gates.

## Sucesso

- Todas as rubricas previstas têm fonte oficial identificada.
- Existe uma fonte estruturada com detalhe suficiente para a árvore escolhida.
- A árvore candidata reconcilia com um total oficial, com diferença máxima de 1 € ou justificação documentada.
- O âmbito pode ser explicado sem interpretação técnica adicional.

## Não sucesso / bloqueio

- O detalhe só existe em PDF sem forma robusta de validar a extração.
- A árvore não cobre o mesmo universo do total apresentado.
- Não é possível distinguir previsão, execução, Administração Central e Segurança Social.

## Critério para avançar

Reduzir o âmbito para uma perspetiva menos granular se a árvore programática não puder ser validada.

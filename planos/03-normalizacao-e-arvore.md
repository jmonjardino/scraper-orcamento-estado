# Parte 3 — Normalização e árvore

## Objetivo final

Converter as fontes em dados navegáveis sem perder códigos, valores, hierarquia ou proveniência.

## O que fazer

- Definir rubrica com identificador, código oficial, designação, cêntimos, ano, dimensão, nível, pai, ordem e fonte.
- Modelar as perspetivas separadamente; não inventar uma árvore universal.
- Implementar importação da árvore canónica e das vistas necessárias.
- Preservar texto oficial e separar rótulos simplificados revistos manualmente.
- Guardar metadados de cobertura e etiquetas factuais de obrigação/vinculação quando existirem na fonte.

## Entregáveis

- Esquema documentado.
- Importador versionado.
- Conjunto OE 2026 normalizado.
- Índice de pesquisa e tabela de proveniência.

## Sucesso

- Todos os nós publicados têm código, designação, valor e fonte.
- Cada filho tem um único pai na sua própria perspetiva.
- Valores mantêm precisão até ao cêntimo.
- O mesmo original gera sempre o mesmo resultado normalizado.

## Não sucesso / bloqueio

- Valores inferidos do layout de PDF.
- Nós sem fonte ou sem dimensão.
- Repetições na mesma árvore sem explicação oficial.

## Critério para avançar

Publicar apenas dimensões com hierarquia e proveniência completas.

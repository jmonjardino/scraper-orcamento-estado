# Parte 2 — Aquisição e arquivo

## Objetivo final

Recolher os ficheiros oficiais de forma repetível, auditável e sem depender de pedidos em tempo real à fonte pública.

## O que fazer

- Limitar a recolha às URLs e domínios oficiais aprovados na Parte 1.
- Preferir XML/XLSX/dados abertos; usar PDF apenas como prova ou fallback assinalado.
- Guardar os originais sem alterações.
- Criar manifestos com URL, data/hora, tipo, tamanho, hash, ano e estado do OE.
- Implementar timeout, tentativas limitadas, limites de frequência e falha segura.
- Tornar o processo idempotente e documentar a atualização anual.

## Entregáveis

- Processo de aquisição repetível.
- Arquivo de originais e manifestos.
- Relatório por recolha.
- Instruções de atualização.

## Implementação

- [Catálogo aprovado OE 2026](../config/fontes-oe2026.json)
- [Adquiridor local](../ferramentas/aquirir_fontes.py)
- [Instruções de aquisição e arquivo](../documentacao/oe2026/aquisicao-e-arquivo.md)

O processo está implementado, mas a aceitação da Parte 2 depende de uma recolha completa e reproduzível. Esta recolha não altera o bloqueio da Parte 1: os PDFs arquivados continuam a ser apenas evidência/fallback, não uma árvore canónica pronta para normalização.

## Sucesso

- Execuções iguais produzem os mesmos hashes quando a fonte não mudou.
- Todos os ficheiros usados constam do manifesto.
- Uma falha parcial não substitui o último conjunto válido.
- A aplicação nunca depende da DGO durante a navegação normal.

## Não sucesso / bloqueio

- A recolha exige sessão autenticada ou intervenção humana frequente.
- Não é possível identificar a versão exata que originou um dado público.

## Critério para avançar

Só avançar quando os dados puderem ser reconstruídos inteiramente a partir dos originais e manifestos arquivados.

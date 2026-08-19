# Normalização e árvore — OE 2026

## Estado e âmbito

`dados/normalizados/oe-2026-approved-initial.json` é o resultado determinista do importador do Mapa 1. Está no estado `normalized_not_validated`; não pode ser servido pela interface nem usado no simulador antes da Parte 4.

A única vista normalizada é `administracao_central_nao_consolidada_por_programa`: Administração Central, não consolidada, despesa orçamentada, Mapa da Lei 1, em euros convertidos para cêntimos inteiros. Exclui a Segurança Social. As vistas funcional, económica e orgânica continuam separadas e não foram inferidas desta fonte.

## Esquema v1

O pacote contém `release`, `view`, `nodes` e `search_index`.

- Cada `budget_node` tem `node_id` estável, `official_code` quando declarado pela fonte, `official_label`, `amount_cents`, ano, dimensão, nível, pai, ordem, terminalidade, etiquetas factuais e `source`.
- `source` liga o nó a `source_id`, hash SHA-256 do manifesto, `locator`, valor e unidade brutos, transformação e natureza (`reported`).
- `plain_label` é sempre separado da designação oficial. Nesta versão é `null`: não foram aprovados rótulos simplificados.
- O campo `source_attributes.ministerio` preserva o Ministério declarado para o programa; não cria um pai orgânico.
- `search_index` contém apenas códigos e designações oficiais dos programas, para pesquisa auditável.

A raiz é necessária para navegação e para impedir ambiguidade no cálculo. O PDF oficial declara-a como `Total da Administração Central`, mas não declara um código. Assim, tem `node_id` técnico estável, `official_code: null` e `official_code_status: not_declared_by_source`; nunca é apresentada como se tivesse um código oficial. Os programas publicados no futuro conservam todos o respetivo código oficial.

## Proveniência e precisão

Os programas vêm de `/Mapa1/Registos/Registo[Programa="…"]/TotalEmEuros` no XML arquivado. A raiz vem do locator `oe2026-mapa1-pdf, página 1, ‘Total da Administração Central’`, declarado no catálogo e ligado ao hash do PDF no manifesto. O importador não lê nem interpreta o layout do PDF.

Todos os montantes são convertidos por `Decimal × 100` e só são aceites se o resultado for um número inteiro de cêntimos. Valores negativos, não finitos, com mais de duas casas decimais, campos obrigatórios em falta, códigos repetidos, cabeçalho incompatível e hashes divergentes fazem o processo falhar.

## Executar

Depois da aquisição:

```bash
python3 ferramentas/normalizar_mapa1.py
```

Para outro arquivo ou destino:

```bash
python3 ferramentas/normalizar_mapa1.py --archive-root /caminho/arquivo --output dados/normalizados/oe-2026-approved-initial.json
```

A saída é escrita atomicamente e só muda se o conteúdo normalizado mudar. O importador não substitui originais nem manifestos.

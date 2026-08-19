# Fontes e inspeção — OE 2026

## Baseline adotada

- Ano: 2026
- Fase: `approved_initial`
- Publicação legal: Lei n.º 73-A/2025, de 30 de dezembro — Orçamento do Estado para 2026.
- Estado: aprovado; não substituir por proposta, execução ou alterações orçamentais.

## Inventário de fontes

| ID | Editor | Artefacto | URL canónico | Formato | Cobertura / uso | Estado de inspeção |
|---|---|---|---|---|---|---|
| `oe2026-lei` | Diário da República | Lei n.º 73-A/2025 | [DR](https://diariodarepublica.pt/dr/detalhe/lei/73-a-2025-993270096-994010475-994010475) · [PDF](https://files.diariodarepublica.pt/1s/2025/12/25002/0000200271.pdf) | HTML/PDF | Fonte legal; o artigo 1.º enumera os mapas. | Adquirida em 2026-08-18; SHA-256 `faccdf07905e46683b538df6dd0e73c6e932f3a73c82d1efeaa3a2caad44223b`. |
| `oe2026-indice-dgo` | DGO | Índice do OE 2026 aprovado | [DGO](https://www.dgo.gov.pt/politicaorcamental/Paginas/OrcamentosEstado.aspx?Ano=2026&TipoOE=Or%C3%A7amento+Estado+Aprovado) | HTML/PDF | Lista Lei, Mapas 1–14, mapas informativos, desenvolvimentos e mapas MBO. | Confirmada em 2026-08-16. |
| `oe2026-mapa1-xml` | Entidade Orçamental | Mapa 1 em formato de dados | [XML](https://www.eo.gov.pt/politicaorcamental/OrcamentodoEstado_ficheirosdeDados/Mapa1-2026.xml) | XML | 20 programas; valores em euros; candidata à vista AC não consolidada por programa. | Adquirida em 2026-08-18; SHA-256 `18bf01da8c851243074644acd2336456da74fd0dcdea467e268c91e9484ff49d`. |
| `oe2026-mapa1-pdf` | Entidade Orçamental | Mapa 1 | [PDF](https://www.eo.gov.pt/politicaorcamental/OrcamentodeEstado/2026/OrcamentoEstadoAprovado/MapasContabilisticos/OE2026_doc02_Mapa01.pdf) | PDF | Evidência do total de referência e do âmbito. | Adquirida em 2026-08-18; SHA-256 `17142be64871020655c4fe58cbfe6d0827cd5bf0e07a7c55c6462d49ae66dd3b`. |
| `oe2026-mbo-acoes` | Entidade Orçamental | Dotações por programa, desdobradas por ações | [PDF](https://www.eo.gov.pt/politicaorcamental/OrcamentodeEstado/2026/OrcamentoEstadoAprovado/DesenvolvimentosOrcamentais/OE2026_MBO_Mapa2.pdf) | PDF | Candidata à hierarquia missão → programa → ação. | Confirmada como PDF; não é ainda fonte estruturada aceite. |
| `oe2026-desenvolvimento-min02` | Entidade Orçamental | Desenvolvimento orçamental da PCM | [PDF](https://www.eo.gov.pt/politicaorcamental/OrcamentodeEstado/2026/OrcamentoEstadoAprovado/DesenvolvimentosOrcamentais/OE2026_MapaAC-DO-Min02.pdf) | PDF | Exemplo de detalhe por ministério e classificação económica. | Confirmada como PDF; referência, não árvore canónica. |
| `oe-dados-dgo` | DGO | Mapas contabilísticos em formato de dados | [DGO](https://www.dgo.gov.pt/politicaorcamental/Paginas/OEpagina_ficheirosdeDados.aspx) | Página de catálogo | Localização oficial indicada para dados/XML. | Em 2026-08-16 não expunha um ficheiro OE 2026 identificável para inspeção. |
| `oe2026-transparencia` | Portal Mais Transparência | Previsão de despesa e receita | [Portal](https://transparencia.gov.pt/pt/orcamento-do-estado/previsao/despesa-receita-previsao/2026/) | HTML/dados abertos | Controlo de âmbito; apresenta despesa efetiva da Administração Central. | Não é fonte de reconciliação da árvore MBO sem compatibilidade demonstrada. |

Os Mapas 2–6 referem-se à Administração Central; os Mapas 7–9 à Segurança Social; o Mapa 1 inclui Administração Central e Segurança Social. Estes universos não podem ser somados ou tratados como equivalentes sem uma reconciliação formal.

## Alteração de endpoint — 2026-08-18

Os dois PDFs estavam inicialmente configurados em `www.dgo.gov.pt`, cuja validação TLS falhou por incompatibilidade do nome no certificado. A página oficial do OE aprovado da [Entidade Orçamental](https://www.eo.gov.pt/politicaorcamental/Paginas/OrcamentosEstado.aspx?Ano=2026&TipoOE=Or%C3%A7amento+Estado+Aprovado) liga para cópias diretas dos mesmos documentos no domínio `www.eo.gov.pt`; esse domínio passa a ser a única origem configurada para os dois PDFs. A aquisição continua a validar TLS normalmente e não aceita certificados inválidos.

## Constatação sobre a árvore

O PDF MBO de ações apresenta a estrutura programática, mas não é um ficheiro estruturado verificável. Além disso, os seus totais publicados pertencem a um âmbito diferente do valor de despesa efetiva consolidada da Administração Central apresentado no Portal Mais Transparência. Portanto, nenhum deles pode ser escolhido como denominador do outro.

O XML `Mapa1-2026` altera esta conclusão para a vista de programas: os seus 20 registos têm código, designação, ministério e total em euros. A soma é 352 472 389 960 €, igual ao `Total da Administração Central` não consolidado no Mapa 1 PDF, página 1. Não contém campo de missão ou de pai, por isso permite `raiz oficial → programa`, não missão → programa → ação.

Consequência: PDFs continuam a ser prova e fallback de auditoria; não serão a fonte primária das folhas. A raiz e o total de referência têm proveniência explícita no Mapa 1 PDF.

## Protocolo reprodutível de inspeção

Executar num diretório temporário, nunca guardar os binários no repositório durante esta parte:

```bash
mkdir -p /tmp/oe2026-inspecao
cd /tmp/oe2026-inspecao

curl --fail --location --remote-name 'https://files.diariodarepublica.pt/1s/2025/12/25002/0000200271.pdf'
curl --fail --location --remote-name 'https://www.eo.gov.pt/politicaorcamental/OrcamentodeEstado/2026/OrcamentoEstadoAprovado/DesenvolvimentosOrcamentais/OE2026_MBO_Mapa2.pdf'
curl --fail --location --remote-name 'https://www.eo.gov.pt/politicaorcamental/OrcamentodeEstado/2026/OrcamentoEstadoAprovado/DesenvolvimentosOrcamentais/OE2026_MapaAC-DO-Min02.pdf'

file *.pdf
sha256sum *.pdf
pdfinfo *.pdf
pdftotext -layout OE2026_MBO_Mapa2.pdf - | sed -n '1,120p'
pdftotext -layout OE2026_MapaAC-DO-Min02.pdf - | sed -n '1,120p'
```

Para um futuro XML/XLSX/CSV disponibilizado pela DGO, registar URL, data/hora UTC, MIME, tamanho e SHA-256, depois validar formato antes de importar:

```bash
xmllint --noout ficheiro.xml
xmllint --format ficheiro.xml | sed -n '1,160p'
unzip -l ficheiro.xlsx
```

Uma aquisição concluída deverá acrescentar hash, tamanho, MIME, timestamp e locators ao inventário. Até isso acontecer, nenhum ficheiro é considerado pronto para importação.

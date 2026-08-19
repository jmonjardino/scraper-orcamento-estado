# Parte 4 — Qualidade e reconciliação

## Objetivo final

Impedir a publicação de valores que não coincidam com as fontes no âmbito declarado.

## O que fazer

- Validar estrutura, formatos, valores, pais e ciclos.
- Validar soma de filhos, subtotais, raiz e totais oficiais.
- Definir tolerância apenas para arredondamento publicado.
- Produzir relatório de reconciliação por importação.
- Controlar estados: recolhido, normalizado, validado, publicado e rejeitado.
- Versionar correções, sem alterar valores silenciosamente.

## Entregáveis

- Suite de validação.
- Relatório de reconciliação OE 2026.
- Metodologia e política de correção.

## Sucesso

- Zero diferenças materiais não explicadas.
- Todas as regras críticas passam antes de publicar.
- Um erro introduzido deliberadamente falha a validação.
- O relatório mostra esperado, calculado, diferença e fonte.

## Não sucesso / bloqueio

- Verificação apenas visual.
- Diferenças escondidas por arredondamento excessivo.
- Não se sabe que versão a aplicação serve.

## Critério para avançar

Só conjuntos no estado `validado` podem chegar à interface.

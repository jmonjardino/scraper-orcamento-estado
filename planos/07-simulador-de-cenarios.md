# Parte 7 — Simulador de cenários

## Objetivo final

Permitir excluir rubricas numa única árvore e apresentar o resultado como cenário orçamental, não como poupança garantida.

## O que fazer

- Definir seleção hierárquica: pai inclui descendentes e exclusão parcial marca pai como parcial.
- Calcular sempre a partir das folhas.
- Mostrar incluído, excluído, percentagem e número de rubricas afetadas.
- Manter cenário apenas no browser nesta versão.
- Mostrar aviso permanente sobre a não equivalência a poupança realizável.
- Mostrar restrições factuais disponíveis antes da exclusão.
- Permitir reset e resumo acessível.
- Impedir mistura de perspetivas; ao trocar de vista, avisar e limpar seleção incompatível.

## Entregáveis

- Seleção por árvore.
- Painel de cenário, avisos e reset.
- Testes contra dupla contagem e estados parciais.

## Sucesso

- Incluído + excluído é exatamente igual ao total de referência, até ao cêntimo.
- Selecionar pai e filho não duplica montante.
- Trocar de perspetiva não preserva seleção incompatível silenciosamente.
- A limitação sobre poupança está presente em todos os fluxos do simulador.

## Não sucesso / bloqueio

- A interface afirma “poupança” como facto.
- Total de cenário não coincide com a raiz validada.
- É possível misturar vista funcional e programática no mesmo cálculo.

## Critério para avançar

Rever o simulador com alguém de contabilidade pública e linguagem clara antes de publicação.

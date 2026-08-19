# Qualidade, reconciliação e governação — OE 2026

## Validação automática

Execute, depois da normalização:

```bash
python3 ferramentas/validar_conjunto_normalizado.py
```

O processo valida campos obrigatórios, códigos, cêntimos inteiros não negativos, âmbito, proveniência, hashes, pais, níveis, ordem entre irmãos, terminalidade e ciclos. Também confirma que o valor bruto da fonte corresponde exatamente ao valor normalizado.

Na vista atual, a soma dos programas é comparada com a raiz e a raiz com o total oficial de referência. A tolerância é **0 cêntimos**: o Mapa 1 fornece valores em euros inteiros e não há ajuste artificial nem arredondamento permissivo.

Cada execução produz `dados/validacoes/<release_id>/<sha256-do-conjunto>.json`. O relatório identifica total esperado, calculado, diferença, tolerância e proveniência em cada controlo financeiro. O nome baseado no hash torna o relatório determinista e impede que uma revisão substitua silenciosamente a evidência de uma versão anterior.

## Estados

O arquivo de fontes está em `collected`; a normalização gera `normalized_not_validated`. Se todas as regras críticas passarem, o relatório recebe `validation_status: validated`; caso contrário recebe `rejected` e o comando termina com erro.

`validated` não equivale a `published`: ao passar, o relatório resolve o gate técnico `part_4_validation_pending`, mas a publicação do OE 2026 continua bloqueada por `reuse_terms_unresolved`. Só um conjunto validado, com bloqueios resolvidos e a aprovação explícita de publicação, pode chegar à interface.

## Política de correção

Não se edita um valor publicado. Uma correção requer novo conjunto normalizado, novo SHA-256 e novo relatório de validação; se já tiver havido publicação, também requer novo `release_id` ou revisão de release documentada. O histórico anterior permanece consultável pelo respetivo hash e pela proveniência original.

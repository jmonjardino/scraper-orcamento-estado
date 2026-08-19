#!/usr/bin/env python3
"""Valida estrutura, proveniência e reconciliação de um conjunto normalizado.

O validador não altera o conjunto de entrada. Produz um relatório imutável cujo
nome contém o SHA-256 do conjunto, para distinguir cada versão corrigida.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
TOLERANCE_CENTS = 0


def canonical_json(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def dataset_sha256(dataset: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(dataset)).hexdigest()


def error(rule: str, message: str, node_id: str | None = None) -> dict[str, str]:
    result = {"rule": rule, "message": message}
    if node_id is not None:
        result["node_id"] = node_id
    return result


def raw_euros_to_cents(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    try:
        cents = Decimal(value) * 100
    except InvalidOperation:
        return None
    if not cents.is_finite() or cents != cents.to_integral_value():
        return None
    return int(cents)


def validate(dataset: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    release = dataset.get("release")
    view = dataset.get("view")
    nodes = dataset.get("nodes")
    if not isinstance(release, dict) or not isinstance(view, dict) or not isinstance(nodes, list):
        errors.append(error("required_top_level_fields", "O conjunto exige release, view e nodes."))
        return report_for(dataset, errors, [])

    required_release = ("release_id", "year", "phase", "publication", "dataset_status")
    for field in required_release:
        if not release.get(field):
            errors.append(error("required_release_field", f"Falta release.{field}."))
    required_view = ("view_id", "dimension", "root_node_id", "coverage", "reference_total")
    for field in required_view:
        if not view.get(field):
            errors.append(error("required_view_field", f"Falta view.{field}."))
    if not isinstance(view.get("coverage"), dict):
        errors.append(error("coverage_object", "view.coverage tem de ser um objeto."))
    else:
        for field in ("institutional_universe", "social_security", "consolidation", "measure", "accounting_classification", "gross_net", "currency", "unit"):
            if not view["coverage"].get(field) or view["coverage"][field] == "unknown":
                errors.append(error("coverage_declared", f"Falta ou é desconhecida a cobertura {field}."))
        if view["coverage"].get("unit") != "cents":
            errors.append(error("currency_unit", "A unidade interna tem de ser cents."))

    by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            errors.append(error("node_object", "Cada nó tem de ser um objeto."))
            continue
        node_id = node.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            errors.append(error("node_id", "Nó sem identificador estável."))
            continue
        if node_id in by_id:
            errors.append(error("unique_node_id", "Identificador de nó repetido.", node_id))
            continue
        by_id[node_id] = node

    root_id = view.get("root_node_id")
    root = by_id.get(root_id)
    if root is None:
        errors.append(error("declared_root", "A raiz declarada não existe."))

    children: dict[str, list[dict[str, Any]]] = {node_id: [] for node_id in by_id}
    seen_codes: set[str] = set()
    for node_id, node in by_id.items():
        required_node = ("official_label", "amount_cents", "year", "dimension", "level", "sort_order", "is_terminal", "source")
        for field in required_node:
            if field not in node or node[field] is None or node[field] == "":
                errors.append(error("required_node_field", f"Falta {field}.", node_id))
        amount = node.get("amount_cents")
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
            errors.append(error("amount_cents", "O montante tem de ser inteiro não negativo em cêntimos.", node_id))
        if node.get("year") != release.get("year") or node.get("dimension") != view.get("dimension"):
            errors.append(error("node_scope", "Ano ou dimensão não coincidem com a vista.", node_id))
        code = node.get("official_code")
        if node_id == root_id:
            if code is not None and not isinstance(code, str):
                errors.append(error("root_official_code", "O código da raiz tem de ser texto ou null.", node_id))
            if code is None and node.get("official_code_status") != "not_declared_by_source":
                errors.append(error("root_official_code", "A exceção de código da raiz tem de ser explícita.", node_id))
        elif not isinstance(code, str) or not code:
            errors.append(error("official_code", "Nós não-raiz exigem código oficial.", node_id))
        elif code in seen_codes:
            errors.append(error("unique_official_code", "Código oficial repetido na vista.", node_id))
        else:
            seen_codes.add(code)

        source = node.get("source")
        if not isinstance(source, dict):
            errors.append(error("provenance", "Nó sem proveniência estruturada.", node_id))
        else:
            for field in ("source_id", "source_sha256", "locator", "raw_value", "raw_unit", "transformation", "kind"):
                if not source.get(field):
                    errors.append(error("provenance", f"Falta source.{field}.", node_id))
            if source.get("raw_unit") != "EUR" or source.get("kind") != "reported":
                errors.append(error("provenance_kind", "A proveniência tem de declarar valor reportado em EUR.", node_id))
            if not isinstance(source.get("source_sha256"), str) or len(source.get("source_sha256", "")) != 64:
                errors.append(error("provenance_hash", "O hash da proveniência tem de ser SHA-256.", node_id))
            raw_cents = raw_euros_to_cents(source.get("raw_value"))
            if raw_cents is None or raw_cents != amount:
                errors.append(error("provenance_amount", "O valor bruto da proveniência não coincide com amount_cents.", node_id))

        parent_id = node.get("parent_node_id")
        if node_id == root_id:
            if parent_id is not None:
                errors.append(error("root_parent", "A raiz não pode ter pai.", node_id))
        elif parent_id not in by_id:
            errors.append(error("valid_parent", "O pai do nó não existe na mesma vista.", node_id))
        else:
            children[parent_id].append(node)
            parent_level = by_id[parent_id].get("level")
            if not isinstance(node.get("level"), int) or node["level"] != parent_level + 1:
                errors.append(error("hierarchy_level", "O nível do filho não é o nível do pai + 1.", node_id))

    for node_id, node in by_id.items():
        has_children = bool(children[node_id])
        if node.get("is_terminal") == has_children:
            errors.append(error("terminality", "is_terminal não coincide com a existência de filhos.", node_id))
        child_orders = [child.get("sort_order") for child in children[node_id]]
        if len(child_orders) != len(set(child_orders)):
            errors.append(error("sibling_sort_order", "Há sort_order repetido entre irmãos.", node_id))

    for node_id in by_id:
        visited: set[str] = set()
        current = node_id
        while current is not None and current in by_id:
            if current in visited:
                errors.append(error("acyclic_hierarchy", "Foi detetado um ciclo de pais.", node_id))
                break
            visited.add(current)
            current = by_id[current].get("parent_node_id")

    financial_checks: list[dict[str, Any]] = []
    for parent_id, child_nodes in children.items():
        if not child_nodes:
            continue
        parent = by_id[parent_id]
        calculated = sum(child["amount_cents"] for child in child_nodes if isinstance(child.get("amount_cents"), int))
        expected = parent.get("amount_cents")
        difference = calculated - expected if isinstance(expected, int) else None
        check = {
            "scope": "children_sum",
            "node_id": parent_id,
            "expected_cents": expected,
            "calculated_cents": calculated,
            "difference_cents": difference,
            "tolerance_cents": TOLERANCE_CENTS,
            "source": parent.get("source"),
            "passed": difference is not None and abs(difference) <= TOLERANCE_CENTS,
        }
        financial_checks.append(check)
        if not check["passed"]:
            errors.append(error("children_sum", "A soma dos filhos não coincide com o subtotal.", parent_id))

    reference = view.get("reference_total") if isinstance(view.get("reference_total"), dict) else {}
    reference_amount = reference.get("amount_cents")
    root_amount = root.get("amount_cents") if root else None
    reference_difference = root_amount - reference_amount if isinstance(root_amount, int) and isinstance(reference_amount, int) else None
    reference_check = {
        "scope": "reference_total",
        "node_id": root_id,
        "expected_cents": reference_amount,
        "calculated_cents": root_amount,
        "difference_cents": reference_difference,
        "tolerance_cents": TOLERANCE_CENTS,
        "source": reference.get("source"),
        "passed": reference_difference is not None and abs(reference_difference) <= TOLERANCE_CENTS,
    }
    financial_checks.append(reference_check)
    if not reference_check["passed"]:
        errors.append(error("reference_total", "A raiz não coincide com o total oficial de referência.", root_id))

    return report_for(dataset, errors, financial_checks)


def report_for(dataset: dict[str, Any], errors: list[dict[str, str]], financial_checks: list[dict[str, Any]]) -> dict[str, Any]:
    dataset_hash = dataset_sha256(dataset)
    release = dataset.get("release") if isinstance(dataset.get("release"), dict) else {}
    view = dataset.get("view") if isinstance(dataset.get("view"), dict) else {}
    validated = not errors
    configured_blockers = view.get("publication_blockers", []) if isinstance(view.get("publication_blockers", []), list) else []
    blockers = [blocker for blocker in configured_blockers if blocker != "part_4_validation_pending" or not validated]
    return {
        "schema_version": SCHEMA_VERSION,
        "validation_status": "validated" if validated else "rejected",
        "publication_status": "blocked" if blockers else "not_assessed",
        "release_id": release.get("release_id"),
        "view_id": view.get("view_id"),
        "dataset_sha256": dataset_hash,
        "tolerance_cents": TOLERANCE_CENTS,
        "critical_rules_passed": validated,
        "effective_publication_blockers": blockers,
        "errors": errors,
        "financial_reconciliation": financial_checks,
    }


def write_if_changed(path: Path, content: bytes) -> bool:
    if path.exists() and path.read_bytes() == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("dados/normalizados/oe-2026-approved-initial.json"))
    parser.add_argument("--reports-root", type=Path, default=Path("dados/validacoes"))
    arguments = parser.parse_args()
    try:
        dataset = json.loads(arguments.input.read_text(encoding="utf-8"))
        report = validate(dataset)
        report_path = arguments.reports_root / str(report["release_id"]) / f"{report['dataset_sha256']}.json"
        changed = write_if_changed(report_path, canonical_json(report))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Erro de validação: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": report["validation_status"], "report": str(report_path), "changed": changed}, ensure_ascii=False))
    return 0 if report["validation_status"] == "validated" else 1


if __name__ == "__main__":
    raise SystemExit(main())

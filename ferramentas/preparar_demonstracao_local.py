#!/usr/bin/env python3
"""Prepara dados reais para uma demonstração pessoal, apenas local.

Este comando não é um atalho para publicação. Exige a validação técnica e a
reconciliação do conjunto, mas preserva todos os bloqueios de reutilização e
aprovação que impedem uma release pública.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_PUBLICATION_SPEC = importlib.util.spec_from_file_location(
    "preparar_publicacao_web", Path(__file__).with_name("preparar_publicacao_web.py")
)
assert _PUBLICATION_SPEC is not None and _PUBLICATION_SPEC.loader is not None
_PUBLICATION_MODULE = importlib.util.module_from_spec(_PUBLICATION_SPEC)
_PUBLICATION_SPEC.loader.exec_module(_PUBLICATION_MODULE)

PublicationError = _PUBLICATION_MODULE.PublicationError
canonical_json = _PUBLICATION_MODULE.canonical_json
dataset_sha256 = _PUBLICATION_MODULE.dataset_sha256
load_json = _PUBLICATION_MODULE.load_json
publication_payload = _PUBLICATION_MODULE.publication_payload
write_atomic = _PUBLICATION_MODULE.write_atomic


DEMO_NOTICE = (
    "Demonstração pessoal local com dados do OE 2026. Não é uma publicação oficial "
    "nem uma redistribuição autorizada; não partilhe esta compilação."
)


def validate_demo(dataset: dict[str, Any], report: dict[str, Any], catalog: dict[str, Any]) -> tuple[str, dict[str, dict[str, Any]]]:
    reasons: list[str] = []
    release = dataset.get("release") if isinstance(dataset.get("release"), dict) else {}
    view = dataset.get("view") if isinstance(dataset.get("view"), dict) else {}
    catalog_release = catalog.get("release") if isinstance(catalog.get("release"), dict) else {}
    dataset_hash = dataset_sha256(dataset)

    if report.get("dataset_sha256") != dataset_hash:
        reasons.append("dataset_sha256_mismatch")
    if report.get("release_id") != release.get("release_id") or catalog_release.get("release_id") != release.get("release_id"):
        reasons.append("release_id_mismatch")
    if report.get("view_id") != view.get("view_id"):
        reasons.append("view_id_mismatch")
    if report.get("validation_status") != "validated" or report.get("critical_rules_passed") is not True or report.get("errors") != []:
        reasons.append("technical_validation_not_passed")

    nodes = dataset.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        reasons.append("dataset_nodes_empty")
        nodes = []
    parent_ids = {node.get("parent_node_id") for node in nodes if isinstance(node, dict) and node.get("parent_node_id") is not None}
    required = {("reference_total", view.get("root_node_id"))} | {("children_sum", node_id) for node_id in parent_ids}
    entries = report.get("financial_reconciliation")
    covered = {
        (entry.get("scope"), entry.get("node_id"))
        for entry in entries if isinstance(entries, list) and isinstance(entry, dict) and entry.get("passed") is True
    }
    if not required.issubset(covered):
        reasons.append("financial_reconciliation_not_passed")

    artifacts = catalog.get("artifacts")
    source_catalog = {
        str(artifact["source_id"]): artifact
        for artifact in artifacts
        if isinstance(artifacts, list) and isinstance(artifact, dict) and isinstance(artifact.get("source_id"), str)
    }
    if not source_catalog:
        reasons.append("source_catalog_empty")
    source_ids = {
        node.get("source", {}).get("source_id")
        for node in nodes if isinstance(node, dict) and isinstance(node.get("source"), dict)
    }
    if not source_ids.issubset(source_catalog):
        reasons.append("source_missing_from_catalog")
    if reasons:
        raise PublicationError(reasons)
    return dataset_hash, source_catalog


def prepare(dataset_path: Path, report_path: Path, catalog_path: Path, output_root: Path) -> Path:
    reasons: list[str] = []
    dataset = load_json(dataset_path, "dataset", reasons)
    report = load_json(report_path, "validation_report", reasons)
    catalog = load_json(catalog_path, "source_catalog", reasons)
    if reasons or dataset is None or report is None or catalog is None:
        raise PublicationError(reasons)
    dataset_hash, source_catalog = validate_demo(dataset, report, catalog)
    payload = publication_payload(dataset, dataset_hash, source_catalog)
    payload["demo"] = {"mode": "personal_local", "notice": DEMO_NOTICE}
    current_path = output_root / "current.json"
    write_atomic(current_path, canonical_json(payload))
    return current_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("dados/normalizados/oe-2026-approved-initial.json"))
    parser.add_argument("--report", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("config/fontes-oe2026.json"))
    parser.add_argument("--output-root", type=Path, default=Path(".generated/demo/public/data"))
    arguments = parser.parse_args()
    try:
        dataset = json.loads(arguments.dataset.read_text(encoding="utf-8"))
        dataset_hash = dataset_sha256(dataset)
        report_path = arguments.report or Path("dados/validacoes") / dataset["release"]["release_id"] / f"{dataset_hash}.json"
        current = prepare(arguments.dataset, report_path, arguments.catalog, arguments.output_root)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"Demonstração local bloqueada:\n- dataset_invalid: {exc}", file=sys.stderr)
        return 1
    except PublicationError as exc:
        print("Demonstração local bloqueada:", file=sys.stderr)
        for reason in exc.reasons:
            print(f"- {reason}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "prepared_for_personal_local_demo", "current": str(current)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

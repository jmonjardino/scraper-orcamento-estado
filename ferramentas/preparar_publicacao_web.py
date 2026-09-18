#!/usr/bin/env python3
"""Cria o único pacote de dados autorizado para a aplicação web.

O empacotador aplica o gate de publicação sobre o conjunto normalizado, o
relatório de validação, o catálogo de fontes e uma aprovação humana vinculada
ao SHA-256 exato do conjunto. Se alguma condição falhar, não escreve outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = 2


class PublicationError(Exception):
    """O gate de publicação não foi satisfeito."""

    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


def canonical_json(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def dataset_sha256(dataset: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(dataset)).hexdigest()


def load_json(path: Path, label: str, reasons: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        reasons.append(f"{label}_missing: {path}")
        return None
    except (OSError, json.JSONDecodeError) as exc:
        reasons.append(f"{label}_invalid: {path}: {exc}")
        return None
    if not isinstance(value, dict):
        reasons.append(f"{label}_invalid: o conteúdo tem de ser um objeto JSON")
        return None
    return value


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def valid_iso8601_datetime(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def valid_reuse_evidence(artifact: dict[str, Any]) -> bool:
    """Confirma que uma licença resolvida é atribuível ao recurso exato."""
    evidence = artifact.get("reuse_evidence")
    if not isinstance(evidence, dict):
        return False
    resource_url = evidence.get("resource_url")
    license_url = evidence.get("license_url")
    statement = evidence.get("statement")
    if resource_url != artifact.get("url") or not isinstance(statement, str) or not statement.strip():
        return False
    if not valid_iso8601_datetime(evidence.get("checked_at")):
        return False
    for url in (resource_url, license_url):
        parsed = urlparse(str(url))
        if parsed.scheme != "https" or not parsed.hostname:
            return False
    return True


def validate_gate(
    dataset: dict[str, Any],
    report: dict[str, Any],
    catalog: dict[str, Any],
    approval: dict[str, Any] | None,
) -> tuple[str, dict[str, dict[str, Any]]]:
    reasons: list[str] = []
    release = dataset.get("release") if isinstance(dataset.get("release"), dict) else {}
    view = dataset.get("view") if isinstance(dataset.get("view"), dict) else {}
    catalog_release = catalog.get("release") if isinstance(catalog.get("release"), dict) else {}
    release_id = release.get("release_id")
    view_id = view.get("view_id")
    actual_hash = dataset_sha256(dataset)

    if not valid_sha256(report.get("dataset_sha256")) or report.get("dataset_sha256") != actual_hash:
        reasons.append("dataset_sha256_mismatch")
    if report.get("release_id") != release_id or catalog_release.get("release_id") != release_id:
        reasons.append("release_id_mismatch")
    if report.get("view_id") != view_id:
        reasons.append("view_id_mismatch")

    if report.get("validation_status") != "validated":
        reasons.append("validation_not_validated")
    if report.get("critical_rules_passed") is not True:
        reasons.append("critical_rules_not_passed")
    if report.get("errors") != []:
        reasons.append("validation_errors_not_empty")
    nodes = dataset.get("nodes")
    parent_node_ids: set[Any] = set()
    if isinstance(nodes, list):
        parent_node_ids = {
            node.get("parent_node_id")
            for node in nodes if isinstance(node, dict) and node.get("parent_node_id") is not None
        }
    required_reconciliations = {("reference_total", view.get("root_node_id"))}
    required_reconciliations.update(("children_sum", node_id) for node_id in parent_node_ids)

    reconciliations = report.get("financial_reconciliation")
    covered_reconciliations: set[tuple[str, Any]] = set()
    reconciliation_invalid = not isinstance(reconciliations, list) or not reconciliations
    if isinstance(reconciliations, list):
        for entry in reconciliations:
            if not isinstance(entry, dict) or entry.get("passed") is not True:
                reconciliation_invalid = True
                continue
            reconciliation = (entry.get("scope"), entry.get("node_id"))
            if reconciliation not in required_reconciliations:
                reconciliation_invalid = True
                continue
            covered_reconciliations.add(reconciliation)
    if reconciliation_invalid:
        reasons.append("financial_reconciliation_failed")
    missing_reconciliations = required_reconciliations - covered_reconciliations
    for scope, node_id in sorted(missing_reconciliations, key=lambda item: (item[0], str(item[1]))):
        reasons.append(f"{scope}_reconciliation_missing:{node_id}")
    blockers = report.get("effective_publication_blockers")
    if not isinstance(blockers, list):
        reasons.append("publication_blockers_invalid")
    elif blockers:
        reasons.extend(f"publication_blocker:{blocker}" for blocker in blockers)
    dataset_blockers = view.get("publication_blockers")
    if not isinstance(dataset_blockers, list):
        reasons.append("dataset_publication_blockers_invalid")
    else:
        for blocker in dataset_blockers:
            reasons.append(f"dataset_publication_blocker:{blocker}")
    if view.get("publication_eligible") is not True:
        reasons.append("publication_eligible_not_true")
    if not isinstance(view.get("selectable"), bool):
        reasons.append("view_selectable_invalid")

    if (
        catalog_release.get("year") != release.get("year")
        or catalog_release.get("phase") != release.get("phase")
        or catalog_release.get("publication") != release.get("publication")
    ):
        reasons.append("release_metadata_mismatch")

    allowed_domains = catalog_release.get("allowed_domains")
    allowed_domains_set = set(allowed_domains) if isinstance(allowed_domains, list) else set()
    source_catalog: dict[str, dict[str, Any]] = {}
    artifacts = catalog.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        reasons.append("source_catalog_empty")
    else:
        for artifact in artifacts:
            if not isinstance(artifact, dict) or not artifact.get("source_id"):
                reasons.append("source_catalog_entry_invalid")
                continue
            source_id = str(artifact["source_id"])
            if source_id in source_catalog:
                reasons.append(f"source_id_duplicate:{source_id}")
                continue
            source_catalog[source_id] = artifact
            for field in ("publisher", "title", "coverage"):
                if not isinstance(artifact.get(field), str) or not artifact[field].strip():
                    reasons.append(f"source_metadata_missing:{source_id}:{field}")
            parsed_url = urlparse(str(artifact.get("url", "")))
            if parsed_url.scheme != "https" or not parsed_url.hostname or parsed_url.hostname not in allowed_domains_set:
                reasons.append(f"source_not_official_https:{source_id}")
            reuse_terms = artifact.get("reuse_terms")
            if not isinstance(reuse_terms, str) or reuse_terms.strip().lower() in {
                "",
                "unresolved",
                "unknown",
                "pending",
                "to_be_confirmed",
            }:
                reasons.append(f"reuse_terms_unresolved:{source_id}")
            elif not valid_reuse_evidence(artifact):
                reasons.append(f"reuse_evidence_invalid:{source_id}")

    if not isinstance(nodes, list) or not nodes:
        reasons.append("dataset_nodes_empty")
    else:
        for node in nodes:
            node_id = node.get("node_id") if isinstance(node, dict) else None
            if not isinstance(node, dict) or not isinstance(node.get("is_terminal"), bool):
                reasons.append(f"node_is_terminal_invalid:{node_id}")
            factual_tags = node.get("factual_tags") if isinstance(node, dict) else None
            if (
                not isinstance(factual_tags, list)
                or any(not isinstance(tag, str) or not tag.strip() for tag in factual_tags)
            ):
                reasons.append(f"node_factual_tags_invalid:{node_id}")
            source = node.get("source") if isinstance(node, dict) and isinstance(node.get("source"), dict) else {}
            source_id = source.get("source_id")
            if source_id not in source_catalog:
                reasons.append(f"source_missing_from_catalog:{source_id}")

    reference = view.get("reference_total") if isinstance(view.get("reference_total"), dict) else {}
    reference_source = reference.get("source") if isinstance(reference.get("source"), dict) else {}
    if reference_source.get("source_id") not in source_catalog:
        reasons.append(f"source_missing_from_catalog:{reference_source.get('source_id')}")

    if approval is None:
        reasons.append("human_approval_missing")
    else:
        if approval.get("schema_version") != 1:
            reasons.append("human_approval_schema_invalid")
        if approval.get("decision") != "approved":
            reasons.append("human_approval_not_approved")
        if approval.get("dataset_sha256") != actual_hash:
            reasons.append("human_approval_sha256_mismatch")
        if approval.get("release_id") != release_id or approval.get("view_id") != view_id:
            reasons.append("human_approval_scope_mismatch")
        approved_by = approval.get("approved_by")
        approved_at = approval.get("approved_at")
        if not isinstance(approved_by, str) or not approved_by.strip():
            reasons.append("human_approval_approved_by_invalid")
        if not valid_iso8601_datetime(approved_at):
            reasons.append("human_approval_approved_at_invalid")

    if reasons:
        raise PublicationError(list(dict.fromkeys(reasons)))
    return actual_hash, source_catalog


def publication_payload(
    dataset: dict[str, Any],
    dataset_hash: str,
    source_catalog: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    release = dataset["release"]
    view = dataset["view"]
    source_ids = sorted({node["source"]["source_id"] for node in dataset["nodes"]})
    sources = [
        {
            "source_id": source_id,
            "publisher": source_catalog[source_id]["publisher"],
            "title": source_catalog[source_id]["title"],
            "url": source_catalog[source_id]["url"],
            "coverage": source_catalog[source_id]["coverage"],
            "reuse_terms": source_catalog[source_id]["reuse_terms"],
        }
        for source_id in source_ids
    ]
    nodes = [
        {
            "node_id": node["node_id"],
            "official_code": node.get("official_code"),
            "official_label": node["official_label"],
            "amount_cents": node["amount_cents"],
            "level": node["level"],
            "parent_node_id": node.get("parent_node_id"),
            "sort_order": node["sort_order"],
            "is_terminal": node["is_terminal"],
            "factual_tags": node["factual_tags"],
            "source": {
                "source_id": node["source"]["source_id"],
                "locator": node["source"]["locator"],
            },
        }
        for node in sorted(dataset["nodes"], key=lambda entry: (entry["level"], entry["sort_order"], entry["node_id"]))
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_sha256": dataset_hash,
        "release": {
            "release_id": release["release_id"],
            "year": release["year"],
            "phase": release["phase"],
            "publication": release["publication"],
        },
        "view": {
            "view_id": view["view_id"],
            "official_name": view["official_name"],
            "dimension": view["dimension"],
            "root_node_id": view["root_node_id"],
            "selectable": view["selectable"],
            "coverage": view["coverage"],
        },
        "nodes": nodes,
        "sources": sources,
    }


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def prepare(
    dataset_path: Path,
    report_path: Path,
    catalog_path: Path,
    approval_path: Path,
    output_root: Path,
) -> tuple[Path, Path]:
    loading_reasons: list[str] = []
    dataset = load_json(dataset_path, "dataset", loading_reasons)
    report = load_json(report_path, "validation_report", loading_reasons)
    catalog = load_json(catalog_path, "source_catalog", loading_reasons)
    approval_loading_reasons: list[str] = []
    approval = load_json(approval_path, "human_approval", approval_loading_reasons)
    if approval is None and all(reason.startswith("human_approval_missing:") for reason in approval_loading_reasons):
        approval_loading_reasons.clear()
    if loading_reasons or dataset is None or report is None or catalog is None:
        raise PublicationError(loading_reasons + approval_loading_reasons)

    try:
        dataset_hash, source_catalog = validate_gate(dataset, report, catalog, approval)
    except PublicationError as exc:
        raise PublicationError(list(dict.fromkeys(approval_loading_reasons + exc.reasons))) from exc
    payload = canonical_json(publication_payload(dataset, dataset_hash, source_catalog))
    current_path = output_root / "current.json"
    release_path = output_root / "releases" / f"{dataset_hash}.json"
    write_atomic(release_path, payload)
    write_atomic(current_path, payload)
    return current_path, release_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("dados/normalizados/oe-2026-approved-initial.json"))
    parser.add_argument("--report", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("config/fontes-oe2026.json"))
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--output-root", type=Path, default=Path(".generated/public/data"))
    arguments = parser.parse_args()
    try:
        dataset_for_paths = json.loads(arguments.dataset.read_text(encoding="utf-8"))
        release_id = dataset_for_paths["release"]["release_id"]
        dataset_hash = dataset_sha256(dataset_for_paths)
        report_path = arguments.report or Path("dados/validacoes") / release_id / f"{dataset_hash}.json"
        approval_path = arguments.approval or Path("config/aprovacoes") / f"{release_id}.json"
        current_path, release_path = prepare(
            arguments.dataset,
            report_path,
            arguments.catalog,
            approval_path,
            arguments.output_root,
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"Publicação web bloqueada:\n- dataset_invalid: {exc}", file=sys.stderr)
        return 1
    except PublicationError as exc:
        print("Publicação web bloqueada:", file=sys.stderr)
        for reason in exc.reasons:
            print(f"- {reason}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "prepared", "current": str(current_path), "release": str(release_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

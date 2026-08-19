#!/usr/bin/env python3
"""Inspeciona o XML oficial Mapa 1 sem o transformar em dados de produto."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


def find_artifact(manifest: dict, source_id: str) -> dict:
    for artifact in manifest["artifacts"]:
        if artifact["source_id"] == source_id:
            return artifact
    raise ValueError(f"O manifesto não contém {source_id}.")


def text(element: ET.Element | None) -> str | None:
    return element.text.strip() if element is not None and element.text else None


def inspect(xml_path: Path) -> dict:
    root = ET.parse(xml_path).getroot()
    if root.tag != "Mapa1":
        raise ValueError(f"Raiz XML inesperada: {root.tag}")
    header = root.find("Cabecalho")
    records = root.findall("./Registos/Registo")
    fields = Counter(field.tag for record in records for field in record)
    totals: list[Decimal] = []
    invalid_totals = 0
    for record in records:
        raw_total = text(record.find("TotalEmEuros"))
        if raw_total is None:
            invalid_totals += 1
            continue
        try:
            totals.append(Decimal(raw_total))
        except InvalidOperation:
            invalid_totals += 1
    required_fields = {"Programa", "DesignacaoPrograma", "Ministério", "TotalEmEuros"}
    return {
        "schema_version": 1,
        "root": root.tag,
        "header": {child.tag: text(child) for child in header} if header is not None else {},
        "record_count": len(records),
        "fields": dict(sorted(fields.items())),
        "required_fields_present": sorted(required_fields.intersection(fields)),
        "required_fields_missing": sorted(required_fields.difference(fields)),
        "distinct_program_codes": len({text(record.find("Programa")) for record in records if text(record.find("Programa"))}),
        "records_with_total": len(totals),
        "records_with_invalid_total": invalid_totals,
        "sum_total_euros": str(sum(totals, Decimal("0"))),
        "has_explicit_mission_field": any("miss" in field.lower() for field in fields),
        "has_explicit_parent_field": any("pai" in field.lower() or "parent" in field.lower() for field in fields),
        "conclusion": "inspection_only_not_a_release_acceptance",
    }


def validate_against_catalog(report: dict, catalog: dict) -> dict:
    artifact = find_artifact(catalog, "oe2026-mapa1-xml")
    expected_total = artifact.get("reference_total_euros")
    checks = {
        "year_is_2026": report["header"].get("Ano") == "2026",
        "map_is_1": report["header"].get("NumeroMapa") == "1",
        "all_required_fields_present": not report["required_fields_missing"],
        "program_codes_are_unique": report["record_count"] == report["distinct_program_codes"],
        "all_totals_are_valid": report["records_with_invalid_total"] == 0,
        "sum_matches_reference_total": report["sum_total_euros"] == expected_total,
    }
    return {
        "reference_total_euros": expected_total,
        "reference_total_scope": artifact.get("reference_total_scope"),
        "reference_locator": artifact.get("reference_locator"),
        "checks": checks,
        "tree_candidate": "administracao_central_nao_consolidada_por_programa" if all(checks.values()) else None,
        "publication_status": "blocked_pending_reuse_terms_and_full_gate_review",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, default=Path("arquivo"))
    parser.add_argument("--catalog", type=Path, default=Path("config/fontes-oe2026.json"))
    parser.add_argument("--release-id", default="oe-2026-approved-initial")
    parser.add_argument("--report", type=Path, help="Escreve o relatório JSON neste caminho.")
    arguments = parser.parse_args()
    try:
        manifest_path = arguments.archive_root / arguments.release_id / "manifesto.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifact = find_artifact(manifest, "oe2026-mapa1-xml")
        xml_path = arguments.archive_root / arguments.release_id / artifact["storage_path"]
        report = inspect(xml_path)
        catalog = json.loads(arguments.catalog.read_text(encoding="utf-8"))
        report["validation"] = validate_against_catalog(report, catalog)
        report["source_id"] = artifact["source_id"]
        report["source_sha256"] = artifact["sha256"]
        report["source_url"] = artifact["url"]
    except (OSError, ValueError, KeyError, ET.ParseError, json.JSONDecodeError) as error:
        print(f"Erro de inspeção: {error}", file=sys.stderr)
        return 1
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

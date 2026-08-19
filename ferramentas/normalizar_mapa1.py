#!/usr/bin/env python3
"""Normaliza a vista programática candidata do Mapa 1 do OE 2026.

Este importador lê exclusivamente o XML original identificado no manifesto. Não
extrai valores de PDFs: o total-raiz publicado no pacote é a referência
declarada no catálogo e aponta para o PDF que a reporta.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


NORMALIZER_VERSION = 1
VIEW_ID = "administracao_central_nao_consolidada_por_programa"
XML_SOURCE_ID = "oe2026-mapa1-xml"
REFERENCE_SOURCE_ID = "oe2026-mapa1-pdf"


class NormalizationError(ValueError):
    """O original ou os metadados não permitem produzir dados fiáveis."""


def canonical_json(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def find_artifact(manifest: dict[str, Any], source_id: str) -> dict[str, Any]:
    for artifact in manifest.get("artifacts", []):
        if artifact.get("source_id") == source_id:
            return artifact
    raise NormalizationError(f"O manifesto não contém o artefacto obrigatório {source_id}.")


def source_reference(artifact: dict[str, Any], locator: str, raw_value: str, transformation: str) -> dict[str, Any]:
    return {
        "source_id": artifact["source_id"],
        "source_sha256": artifact["sha256"],
        "locator": locator,
        "raw_value": raw_value,
        "raw_unit": "EUR",
        "transformation": transformation,
        "kind": "reported",
    }


def euros_to_cents(raw_value: str) -> int:
    try:
        value = Decimal(raw_value.strip())
    except (InvalidOperation, AttributeError) as error:
        raise NormalizationError(f"Montante inválido: {raw_value!r}") from error
    if not value.is_finite() or value < 0:
        raise NormalizationError(f"Montante não suportado: {raw_value!r}")
    cents = value * 100
    if cents != cents.to_integral_value():
        raise NormalizationError(f"O montante não tem precisão de cêntimo: {raw_value!r}")
    return int(cents)


def node_id(release_id: str, official_code: str) -> str:
    return f"{release_id}:{VIEW_ID}:programa:{official_code}"


def verify_archived_artifact(archive_root: Path, release_id: str, artifact: dict[str, Any]) -> Path:
    path = archive_root / release_id / artifact["storage_path"]
    try:
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise NormalizationError(f"Não foi possível ler o original arquivado {artifact['source_id']}.") from error
    if actual_hash != artifact["sha256"]:
        raise NormalizationError(f"O hash do original {artifact['source_id']} não coincide com o manifesto.")
    return path


def normalize(manifest: dict[str, Any], catalog: dict[str, Any], archive_root: Path) -> dict[str, Any]:
    release = catalog.get("release", {})
    release_id = release.get("release_id")
    if not release_id or manifest.get("release_id") != release_id:
        raise NormalizationError("O release_id do manifesto não coincide com o catálogo.")
    if manifest.get("year") != release.get("year") or manifest.get("phase") != release.get("phase"):
        raise NormalizationError("Ano ou fase do manifesto não coincidem com o catálogo.")

    xml_artifact = find_artifact(manifest, XML_SOURCE_ID)
    reference_artifact = find_artifact(manifest, REFERENCE_SOURCE_ID)
    xml_path = verify_archived_artifact(archive_root, release_id, xml_artifact)
    verify_archived_artifact(archive_root, release_id, reference_artifact)

    source_catalog = next((item for item in catalog.get("artifacts", []) if item.get("source_id") == XML_SOURCE_ID), None)
    if source_catalog is None:
        raise NormalizationError("O catálogo não contém a fonte XML do Mapa 1.")
    reference_total_raw = source_catalog.get("reference_total_euros")
    reference_locator = source_catalog.get("reference_locator")
    if not isinstance(reference_total_raw, str) or not isinstance(reference_locator, str):
        raise NormalizationError("Falta o total de referência ou o seu locator no catálogo.")

    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError as error:
        raise NormalizationError(f"XML inválido: {error}") from error
    if root.tag != "Mapa1":
        raise NormalizationError(f"Raiz XML inesperada: {root.tag}")
    header_element = root.find("Cabecalho")
    header = {child.tag: (child.text or "").strip() for child in header_element} if header_element is not None else {}
    if header.get("Ano") != str(release["year"]) or header.get("NumeroMapa") != "1":
        raise NormalizationError("O cabeçalho XML não corresponde ao OE 2026, Mapa 1.")

    root_node_id = f"{release_id}:{VIEW_ID}:root"
    nodes: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    for order, record in enumerate(root.findall("./Registos/Registo"), start=1):
        values = {child.tag: (child.text or "").strip() for child in record}
        required = ("Programa", "DesignacaoPrograma", "Ministério", "TotalEmEuros")
        if any(not values.get(field) for field in required):
            raise NormalizationError(f"Registo {order} sem os campos obrigatórios do Mapa 1.")
        code = values["Programa"]
        if code in seen_codes:
            raise NormalizationError(f"Código de programa repetido no Mapa 1: {code}")
        seen_codes.add(code)
        raw_total = values["TotalEmEuros"]
        nodes.append({
            "node_id": node_id(release_id, code),
            "official_code": code,
            "official_label": values["DesignacaoPrograma"],
            "plain_label": None,
            "amount_cents": euros_to_cents(raw_total),
            "year": release["year"],
            "dimension": "programmatic",
            "level": 1,
            "parent_node_id": root_node_id,
            "sort_order": order,
            "is_terminal": True,
            "factual_tags": [],
            "source": source_reference(
                xml_artifact,
                f"/Mapa1/Registos/Registo[Programa={json.dumps(code, ensure_ascii=False)}]/TotalEmEuros",
                raw_total,
                "EUR decimal × 100 -> integer cents",
            ),
            "source_attributes": {"ministerio": values["Ministério"]},
        })
    if not nodes:
        raise NormalizationError("O Mapa 1 não contém programas.")

    reference_total_cents = euros_to_cents(reference_total_raw)
    root_node = {
        "node_id": root_node_id,
        "official_code": None,
        "official_label": "Total da Administração Central",
        "plain_label": None,
        "amount_cents": reference_total_cents,
        "year": release["year"],
        "dimension": "programmatic",
        "level": 0,
        "parent_node_id": None,
        "sort_order": 0,
        "is_terminal": False,
        "factual_tags": [],
        "source": source_reference(reference_artifact, reference_locator, reference_total_raw, "EUR decimal × 100 -> integer cents"),
        "source_attributes": {},
        "official_code_status": "not_declared_by_source",
    }
    all_nodes = [root_node, *nodes]
    search_index = sorted(
        ({"node_id": node["node_id"], "official_code": node["official_code"], "official_label": node["official_label"]} for node in nodes),
        key=lambda entry: (entry["official_code"], entry["node_id"]),
    )
    return {
        "schema_version": 1,
        "normalizer_version": NORMALIZER_VERSION,
        "release": {
            "release_id": release_id,
            "year": release["year"],
            "phase": release["phase"],
            "publication": release["publication"],
            "dataset_status": "normalized_not_validated",
        },
        "view": {
            "view_id": VIEW_ID,
            "dimension": "programmatic",
            "official_name": "Mapa 1 — Despesas por missão de base orgânica, desagregadas por programas",
            "root_node_id": root_node_id,
            "selectable": False,
            "publication_eligible": False,
            "publication_blockers": ["reuse_terms_unresolved", "part_4_validation_pending"],
            "coverage": {
                "institutional_universe": "administracao_central",
                "social_security": "excluded",
                "consolidation": "non_consolidated",
                "measure": "budgeted_expenditure",
                "accounting_classification": "mapa_da_lei_base_organica_por_programa",
                "gross_net": "not_declared_by_source",
                "currency": "EUR",
                "unit": "cents",
            },
            "reference_total": {
                "amount_cents": reference_total_cents,
                "source": root_node["source"],
            },
        },
        "nodes": all_nodes,
        "search_index": search_index,
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
    parser.add_argument("--archive-root", type=Path, default=Path("arquivo"))
    parser.add_argument("--catalog", type=Path, default=Path("config/fontes-oe2026.json"))
    parser.add_argument("--output", type=Path, default=Path("dados/normalizados/oe-2026-approved-initial.json"))
    arguments = parser.parse_args()
    try:
        catalog = json.loads(arguments.catalog.read_text(encoding="utf-8"))
        release_id = catalog["release"]["release_id"]
        manifest = json.loads((arguments.archive_root / release_id / "manifesto.json").read_text(encoding="utf-8"))
        dataset = normalize(manifest, catalog, arguments.archive_root)
        changed = write_if_changed(arguments.output, canonical_json(dataset))
    except (NormalizationError, OSError, KeyError, json.JSONDecodeError) as error:
        print(f"Erro de normalização: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "success", "output": str(arguments.output), "changed": changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

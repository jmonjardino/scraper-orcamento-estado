#!/usr/bin/env python3
"""Arquivo reprodutível dos artefactos oficiais do Orçamento do Estado.

Não normaliza nem interpreta dados orçamentais. Cada execução descarrega apenas
as URLs declaradas no catálogo, valida o resultado e arquiva o original pelo
seu SHA-256. Um manifesto só é publicado depois de todos os artefactos terem
sido adquiridos com sucesso.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import shutil
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class AcquisitionError(RuntimeError):
    """A fonte não pôde ser adquirida ou não corresponde ao catálogo."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_catalog(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        catalog = json.load(handle)
    if not isinstance(catalog.get("artifacts"), list) or not catalog["artifacts"]:
        raise AcquisitionError("O catálogo tem de declarar pelo menos um artefacto.")
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    release = catalog.get("release", {})
    allowed_domains = set(release.get("allowed_domains", []))
    source_ids: set[str] = set()
    for artifact in catalog["artifacts"]:
        source_id = artifact.get("source_id")
        parsed = urlparse(artifact.get("url", ""))
        if not source_id or source_id in source_ids:
            raise AcquisitionError("Cada artefacto tem de ter um source_id único.")
        if parsed.scheme != "https" or parsed.hostname not in allowed_domains:
            raise AcquisitionError(f"URL não aprovada para {source_id}: {artifact.get('url')}")
        if not artifact.get("expected_mime_types"):
            raise AcquisitionError(f"Falta expected_mime_types em {source_id}.")
        source_ids.add(source_id)


def detect_mime(path: Path, header_mime: str | None) -> str:
    with path.open("rb") as handle:
        magic = handle.read(8)
    if magic.startswith(b"%PDF-"):
        return "application/pdf"
    if magic.startswith(b"PK\x03\x04"):
        return "application/zip"
    if magic.lstrip().startswith(b"<"):
        return "application/xml"
    if header_mime:
        return header_mime.split(";", 1)[0].strip().lower()
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def validate_content(artifact: dict[str, Any], path: Path) -> None:
    if artifact["format"] != "xml":
        return
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        raise AcquisitionError(f"XML inválido em {artifact['source_id']}: {error}") from error
    if root.tag != "Mapa1":
        raise AcquisitionError(f"Raiz XML inesperada em {artifact['source_id']}: {root.tag}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def promote_original(source_path: Path, target_path: Path) -> None:
    """Promove um original para o arquivo, mesmo se /tmp estiver noutro volume.

    ``os.replace`` só é atómico no mesmo sistema de ficheiros. Por isso a cópia
    é feita primeiro para um temporário criado ao lado do destino; a promoção
    final mantém-se atómica nesse volume.
    """
    source_hash = sha256_file(source_path)
    if target_path.exists():
        if sha256_file(target_path) != source_hash:
            raise AcquisitionError(f"O arquivo existente não corresponde ao hash esperado: {target_path}")
        return

    target_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with source_path.open("rb") as source, tempfile.NamedTemporaryFile(
            dir=target_path.parent, prefix=f".{target_path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            shutil.copyfileobj(source, temporary)
            temporary.flush()
            os.fsync(temporary.fileno())
        if sha256_file(temporary_path) != source_hash:
            raise AcquisitionError(f"A cópia para o arquivo não preservou o hash: {target_path}")
        os.replace(temporary_path, target_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def download(artifact: dict[str, Any], request_config: dict[str, Any], destination: Path) -> tuple[str, int]:
    attempts = int(request_config["max_attempts"])
    timeout = float(request_config["timeout_seconds"])
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = Request(artifact["url"], headers={"User-Agent": request_config["user_agent"]})
        try:
            with urlopen(request, timeout=timeout) as response, destination.open("wb") as output:
                shutil.copyfileobj(response, output)
                return response.headers.get("Content-Type", ""), response.status
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            last_error = error
            destination.unlink(missing_ok=True)
            if attempt < attempts:
                time.sleep(min(2 ** (attempt - 1), 4))
    raise AcquisitionError(f"Falhou {artifact['source_id']} após {attempts} tentativas: {last_error}")


def artifact_record(artifact: dict[str, Any], path: Path, header_mime: str, http_status: int) -> dict[str, Any]:
    sha256 = sha256_file(path)
    detected_mime = detect_mime(path, header_mime)
    if detected_mime not in artifact["expected_mime_types"]:
        raise AcquisitionError(
            f"MIME inesperado em {artifact['source_id']}: {detected_mime}; esperado: {artifact['expected_mime_types']}"
        )
    validate_content(artifact, path)
    return {
        "source_id": artifact["source_id"],
        "publisher": artifact["publisher"],
        "title": artifact["title"],
        "url": artifact["url"],
        "format": artifact["format"],
        "role": artifact["role"],
        "coverage": artifact["coverage"],
        "reuse_terms": artifact["reuse_terms"],
        "http_status": http_status,
        "header_mime_type": header_mime.split(";", 1)[0].strip().lower() or None,
        "detected_mime_type": detected_mime,
        "size_bytes": path.stat().st_size,
        "sha256": sha256,
        "storage_path": f"originais/sha256/{sha256[:2]}/{sha256}",
    }


def release_manifest(catalog: dict[str, Any], artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    release = catalog["release"]
    return {
        "schema_version": 1,
        "release_id": release["release_id"],
        "year": release["year"],
        "phase": release["phase"],
        "publication": release["publication"],
        "artifacts": sorted(artifacts, key=lambda artifact: artifact["source_id"]),
    }


def write_if_changed(path: Path, content: bytes) -> bool:
    if path.exists() and path.read_bytes() == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)
    return True


def acquire(catalog: dict[str, Any], archive_root: Path, dry_run: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_catalog(catalog)
    release = catalog["release"]
    request_config = release["request"]
    collected: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    last_request_started: float | None = None

    with tempfile.TemporaryDirectory(prefix="oe-acquisition-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        for artifact in catalog["artifacts"]:
            if dry_run:
                collected.append({"source_id": artifact["source_id"], "status": "not_downloaded_dry_run"})
                continue
            if last_request_started is not None:
                remaining = float(request_config["min_interval_seconds"]) - (time.monotonic() - last_request_started)
                if remaining > 0:
                    time.sleep(remaining)
            temporary_file = temporary_root / artifact["source_id"]
            try:
                last_request_started = time.monotonic()
                header_mime, http_status = download(artifact, request_config, temporary_file)
                record = artifact_record(artifact, temporary_file, header_mime, http_status)
                collected.append(record)
            except AcquisitionError as error:
                errors.append({"source_id": artifact["source_id"], "error": str(error)})

        manifest = release_manifest(catalog, collected) if not errors and not dry_run else None
        if manifest is not None:
            for record in collected:
                source_path = temporary_root / record["source_id"]
                target_path = archive_root / release["release_id"] / record["storage_path"]
                promote_original(source_path, target_path)

            manifest_path = archive_root / release["release_id"] / "manifesto.json"
            manifest_changed = write_if_changed(manifest_path, json_bytes(manifest))
        else:
            manifest_changed = False

    report = {
        "schema_version": 1,
        "release_id": release["release_id"],
        "started_at": utc_now(),
        "status": "success" if manifest is not None else "failed" if errors else "dry_run",
        "manifest_published": manifest is not None,
        "manifest_changed": manifest_changed,
        "artifacts": collected,
        "errors": errors,
    }
    reports_directory = archive_root / release["release_id"] / "relatorios"
    report_path = reports_directory / f"{report['started_at'].replace(':', '')}.json"
    write_if_changed(report_path, json_bytes(report))
    return manifest or {}, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("config/fontes-oe2026.json"))
    parser.add_argument("--archive-root", type=Path, default=Path("arquivo"))
    parser.add_argument("--dry-run", action="store_true", help="Valida o catálogo sem fazer pedidos HTTP.")
    arguments = parser.parse_args()
    try:
        catalog = load_catalog(arguments.catalog)
        manifest, report = acquire(catalog, arguments.archive_root, arguments.dry_run)
    except (AcquisitionError, json.JSONDecodeError, KeyError) as error:
        print(f"Erro de aquisição: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": report["status"], "manifest": manifest, "report": report}, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"success", "dry_run"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

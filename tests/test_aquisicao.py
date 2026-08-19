import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aquirir_fontes", ROOT / "ferramentas" / "aquirir_fontes.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class AcquisitionTests(unittest.TestCase):
    def catalog(self, url="https://www.dgo.gov.pt/ficheiro.pdf"):
        return {
            "release": {
                "release_id": "oe-2026-approved-initial",
                "year": 2026,
                "phase": "approved_initial",
                "publication": "Lei n.º 73-A/2025",
                "allowed_domains": ["www.dgo.gov.pt"],
                "request": {"timeout_seconds": 1, "max_attempts": 1, "min_interval_seconds": 0, "user_agent": "test"},
            },
            "artifacts": [{
                "source_id": "fonte", "publisher": "DGO", "title": "Fonte", "url": url,
                "format": "pdf", "role": "fallback_evidence", "coverage": "teste", "reuse_terms": "unresolved",
                "expected_mime_types": ["application/pdf"],
            }],
        }

    def test_catalog_rejeita_dominio_nao_aprovado(self):
        with self.assertRaises(MODULE.AcquisitionError):
            MODULE.validate_catalog(self.catalog("https://example.org/ficheiro.pdf"))

    def test_catalog_oe2026_aceita_apenas_as_origens_oficiais_configuradas(self):
        catalog = MODULE.load_catalog(ROOT / "config" / "fontes-oe2026.json")
        MODULE.validate_catalog(catalog)
        self.assertEqual(
            set(catalog["release"]["allowed_domains"]),
            {"files.diariodarepublica.pt", "www.eo.gov.pt"},
        )

    def test_mime_pdf_e_hash_sao_registados(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fonte"
            path.write_bytes(b"%PDF-1.7\nconteudo")
            record = MODULE.artifact_record(self.catalog()["artifacts"][0], path, "application/pdf", 200)
        self.assertEqual(record["detected_mime_type"], "application/pdf")
        self.assertEqual(record["size_bytes"], 17)
        self.assertEqual(len(record["sha256"]), 64)

    def test_xml_mapa1_e_validado_pela_raiz(self):
        artifact = self.catalog()["artifacts"][0] | {
            "format": "xml", "expected_mime_types": ["application/xml"], "source_id": "mapa1"
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapa1.xml"
            path.write_text("<Mapa1><Cabecalho /></Mapa1>", encoding="utf-8")
            record = MODULE.artifact_record(artifact, path, "text/xml", 200)
        self.assertEqual(record["detected_mime_type"], "application/xml")

    def test_xml_com_raiz_errada_e_rejeitado(self):
        artifact = self.catalog()["artifacts"][0] | {
            "format": "xml", "expected_mime_types": ["application/xml"], "source_id": "mapa1"
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapa1.xml"
            path.write_text("<OutraRaiz />", encoding="utf-8")
            with self.assertRaises(MODULE.AcquisitionError):
                MODULE.artifact_record(artifact, path, "application/xml", 200)

    def test_promocao_copia_para_o_volume_de_destino_e_preserva_hash(self):
        with tempfile.TemporaryDirectory() as source_directory, tempfile.TemporaryDirectory() as archive_directory:
            source = Path(source_directory) / "original.pdf"
            target = Path(archive_directory) / "originais" / "original.pdf"
            source.write_bytes(b"%PDF-1.7\nconteudo")
            MODULE.promote_original(source, target)
            self.assertEqual(MODULE.sha256_file(source), MODULE.sha256_file(target))
            self.assertTrue(source.exists())

    def test_promocao_rejeita_arquivo_existente_com_hash_diferente(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.pdf"
            target = Path(directory) / "target.pdf"
            source.write_bytes(b"%PDF-1.7\noriginal")
            target.write_bytes(b"%PDF-1.7\ncorrompido")
            with self.assertRaises(MODULE.AcquisitionError):
                MODULE.promote_original(source, target)

    def test_manifest_e_determinista(self):
        artifact = {"source_id": "b", "sha256": "2"}
        manifest_a = MODULE.release_manifest(self.catalog(), [artifact, {"source_id": "a", "sha256": "1"}])
        manifest_b = MODULE.release_manifest(self.catalog(), [{"source_id": "a", "sha256": "1"}, artifact])
        self.assertEqual(json.dumps(manifest_a, sort_keys=True), json.dumps(manifest_b, sort_keys=True))

    def test_dry_run_nao_cria_manifesto(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest, report = MODULE.acquire(self.catalog(), Path(directory), dry_run=True)
            self.assertEqual(manifest, {})
            self.assertEqual(report["status"], "dry_run")
            self.assertFalse((Path(directory) / "oe-2026-approved-initial" / "manifesto.json").exists())

    def test_falha_nao_substitui_manifesto_existente(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "oe-2026-approved-initial" / "manifesto.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text('{"estado":"anterior"}\n', encoding="utf-8")
            with patch.object(MODULE, "download", side_effect=MODULE.AcquisitionError("indisponível")):
                manifest, report = MODULE.acquire(self.catalog(), Path(directory))
            self.assertEqual(manifest, {})
            self.assertEqual(report["status"], "failed")
            self.assertEqual(manifest_path.read_text(encoding="utf-8"), '{"estado":"anterior"}\n')

    def test_execucao_igual_mantem_manifesto(self):
        def fake_download(_artifact, _request, destination):
            destination.write_bytes(b"%PDF-1.7\nconteudo")
            return "application/pdf", 200

        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory)
            with patch.object(MODULE, "download", side_effect=fake_download):
                first_manifest, first_report = MODULE.acquire(self.catalog(), archive)
                second_manifest, second_report = MODULE.acquire(self.catalog(), archive)
            manifest_path = archive / "oe-2026-approved-initial" / "manifesto.json"
            self.assertEqual(first_manifest, second_manifest)
            self.assertTrue(first_report["manifest_changed"])
            self.assertFalse(second_report["manifest_changed"])
            self.assertTrue(manifest_path.exists())


if __name__ == "__main__":
    unittest.main()

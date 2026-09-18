import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "preparar_demonstracao_local", ROOT / "ferramentas" / "preparar_demonstracao_local.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class LocalDemoTests(unittest.TestCase):
    def test_prepara_conjunto_validado_sem_remover_bloqueios_publicos(self):
        dataset_path = ROOT / "dados/normalizados/oe-2026-approved-initial.json"
        dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
        dataset_hash = MODULE.dataset_sha256(dataset)
        report_path = ROOT / "dados/validacoes" / dataset["release"]["release_id"] / f"{dataset_hash}.json"
        with tempfile.TemporaryDirectory() as directory_name:
            current = MODULE.prepare(dataset_path, report_path, ROOT / "config/fontes-oe2026.json", Path(directory_name))
            payload = json.loads(current.read_text(encoding="utf-8"))
        self.assertEqual(payload["dataset_sha256"], dataset_hash)
        self.assertEqual(payload["demo"]["mode"], "personal_local")
        self.assertIn("Não é uma publicação oficial", payload["demo"]["notice"])
        self.assertFalse(payload["view"]["selectable"])

    def test_recusa_relatorio_sem_validacao_tecnica(self):
        dataset_path = ROOT / "dados/normalizados/oe-2026-approved-initial.json"
        dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
        dataset_hash = MODULE.dataset_sha256(dataset)
        report_path = ROOT / "dados/validacoes" / dataset["release"]["release_id"] / f"{dataset_hash}.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["validation_status"] = "rejected"
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            changed_report = directory / "report.json"
            changed_report.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(MODULE.PublicationError) as context:
                MODULE.prepare(dataset_path, changed_report, ROOT / "config/fontes-oe2026.json", directory / "out")
        self.assertIn("technical_validation_not_passed", context.exception.reasons)

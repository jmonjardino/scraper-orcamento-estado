import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "preparar_publicacao_web", ROOT / "ferramentas" / "preparar_publicacao_web.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def source(source_id: str, raw_value: str = "20"):
    return {
        "source_id": source_id,
        "source_sha256": "a" * 64,
        "locator": f"/{source_id}/valor",
        "raw_value": raw_value,
        "raw_unit": "EUR",
        "transformation": "EUR decimal × 100 -> integer cents",
        "kind": "reported",
    }


def fixture():
    root_id = "release:view:root"
    dataset = {
        "schema_version": 1,
        "release": {
            "release_id": "release",
            "year": 2026,
            "phase": "approved_initial",
            "publication": "Lei",
            "dataset_status": "normalized_not_validated",
        },
        "view": {
            "view_id": "view",
            "official_name": "Mapa de teste",
            "dimension": "programmatic",
            "root_node_id": root_id,
            "publication_blockers": [],
            "publication_eligible": True,
            "coverage": {
                "institutional_universe": "administracao_central",
                "social_security": "excluded",
                "consolidation": "non_consolidated",
                "measure": "budgeted_expenditure",
                "accounting_classification": "mapa",
                "gross_net": "not_declared_by_source",
                "currency": "EUR",
                "unit": "cents",
            },
            "reference_total": {"amount_cents": 2000, "source": source("mapa-pdf")},
        },
        "nodes": [
            {
                "node_id": root_id,
                "official_code": None,
                "official_label": "Total",
                "amount_cents": 2000,
                "level": 0,
                "parent_node_id": None,
                "sort_order": 0,
                "source": source("mapa-pdf"),
            },
            {
                "node_id": "release:view:P-001",
                "official_code": "P-001",
                "official_label": "Programa",
                "amount_cents": 2000,
                "level": 1,
                "parent_node_id": root_id,
                "sort_order": 1,
                "source": source("mapa-xml"),
            },
        ],
    }
    dataset_hash = MODULE.dataset_sha256(dataset)
    report = {
        "dataset_sha256": dataset_hash,
        "release_id": "release",
        "view_id": "view",
        "validation_status": "validated",
        "critical_rules_passed": True,
        "errors": [],
        "financial_reconciliation": [
            {"scope": "children_sum", "node_id": root_id, "passed": True},
            {"scope": "reference_total", "node_id": root_id, "passed": True},
        ],
        "effective_publication_blockers": [],
    }
    catalog = {
        "release": {
            "release_id": "release",
            "year": 2026,
            "phase": "approved_initial",
            "publication": "Lei",
            "allowed_domains": ["dados.gov.pt"],
        },
        "artifacts": [
            {
                "source_id": source_id,
                "publisher": "Entidade oficial",
                "title": title,
                "url": f"https://dados.gov.pt/{source_id}",
                "coverage": "Teste",
                "reuse_terms": "public_domain",
            }
            for source_id, title in (("mapa-pdf", "Mapa PDF"), ("mapa-xml", "Mapa XML"))
        ],
    }
    approval = {
        "schema_version": 1,
        "decision": "approved",
        "dataset_sha256": dataset_hash,
        "release_id": "release",
        "view_id": "view",
        "approved_by": "Pessoa revisora",
        "approved_at": "2026-08-18T20:00:00Z",
    }
    return dataset, report, catalog, approval


def write_fixture(directory: Path, dataset, report, catalog, approval):
    paths = {}
    for name, value in (("dataset", dataset), ("report", report), ("catalog", catalog), ("approval", approval)):
        path = directory / f"{name}.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        paths[name] = path
    return paths


class WebPublicationTests(unittest.TestCase):
    def test_gate_aceita_apenas_todas_as_condicoes_e_output_e_determinista(self):
        dataset, report, catalog, approval = fixture()
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            paths = write_fixture(directory, dataset, report, catalog, approval)
            output = directory / "out"
            current, release = MODULE.prepare(**{f"{name}_path": path for name, path in paths.items()}, output_root=output)
            first_current = current.read_bytes()
            first_release = release.read_bytes()
            MODULE.prepare(**{f"{name}_path": path for name, path in paths.items()}, output_root=output)
            self.assertEqual(first_current, current.read_bytes())
            self.assertEqual(first_release, release.read_bytes())
            self.assertEqual(first_current, first_release)
            payload = json.loads(first_current)
            self.assertEqual(payload["dataset_sha256"], MODULE.dataset_sha256(dataset))
            self.assertNotIn("dataset_status", payload["release"])

    def test_hash_release_e_view_têm_de_coincidir(self):
        dataset, report, catalog, approval = fixture()
        report["dataset_sha256"] = "f" * 64
        report["release_id"] = "outro"
        report["view_id"] = "outra"
        with self.assertRaises(MODULE.PublicationError) as context:
            MODULE.validate_gate(dataset, report, catalog, approval)
        self.assertTrue(
            {"dataset_sha256_mismatch", "release_id_mismatch", "view_id_mismatch"}.issubset(context.exception.reasons)
        )

    def test_validação_reconciliações_blockers_e_elegibilidade_são_obrigatórios(self):
        dataset, report, catalog, approval = fixture()
        report |= {
            "validation_status": "rejected",
            "critical_rules_passed": False,
            "financial_reconciliation": [{"passed": False}],
            "effective_publication_blockers": ["diferença_material"],
        }
        dataset["view"]["publication_eligible"] = False
        dataset["view"]["publication_blockers"] = ["gate_manual"]
        with self.assertRaises(MODULE.PublicationError) as context:
            MODULE.validate_gate(dataset, report, catalog, approval)
        self.assertTrue(
            {
                "validation_not_validated",
                "critical_rules_not_passed",
                "financial_reconciliation_failed",
                "publication_blocker:diferença_material",
                "dataset_publication_blocker:gate_manual",
                "publication_eligible_not_true",
            }.issubset(context.exception.reasons)
        )

    def test_reconciliacao_reference_total_da_raiz_e_obrigatoria(self):
        dataset, report, catalog, approval = fixture()
        report["financial_reconciliation"] = [
            entry for entry in report["financial_reconciliation"] if entry["scope"] != "reference_total"
        ]
        with self.assertRaises(MODULE.PublicationError) as context:
            MODULE.validate_gate(dataset, report, catalog, approval)
        self.assertIn(
            f"reference_total_reconciliation_missing:{dataset['view']['root_node_id']}",
            context.exception.reasons,
        )

    def test_reconciliacao_children_sum_de_cada_pai_e_obrigatoria(self):
        dataset, report, catalog, approval = fixture()
        report["financial_reconciliation"] = [
            entry for entry in report["financial_reconciliation"] if entry["scope"] != "children_sum"
        ]
        with self.assertRaises(MODULE.PublicationError) as context:
            MODULE.validate_gate(dataset, report, catalog, approval)
        self.assertIn(
            f"children_sum_reconciliation_missing:{dataset['view']['root_node_id']}",
            context.exception.reasons,
        )

    def test_reconciliacao_children_sum_cobre_tambem_pais_intermedios(self):
        dataset, report, catalog, approval = fixture()
        intermediate_id = dataset["nodes"][1]["node_id"]
        dataset["nodes"].append(
            {
                "node_id": "release:view:P-001:filho",
                "official_code": "P-001.1",
                "official_label": "Ação",
                "amount_cents": 2000,
                "level": 2,
                "parent_node_id": intermediate_id,
                "sort_order": 1,
                "source": source("mapa-xml"),
            }
        )
        dataset_hash = MODULE.dataset_sha256(dataset)
        report["dataset_sha256"] = dataset_hash
        approval["dataset_sha256"] = dataset_hash
        with self.assertRaises(MODULE.PublicationError) as context:
            MODULE.validate_gate(dataset, report, catalog, approval)
        self.assertIn(f"children_sum_reconciliation_missing:{intermediate_id}", context.exception.reasons)

    def test_reconciliacao_com_scope_ou_no_errado_nao_satisfaz_cobertura(self):
        dataset, report, catalog, approval = fixture()
        report["financial_reconciliation"][0] = {
            "scope": "children_sum",
            "node_id": "release:view:not-a-parent",
            "passed": True,
        }
        with self.assertRaises(MODULE.PublicationError) as context:
            MODULE.validate_gate(dataset, report, catalog, approval)
        self.assertIn("financial_reconciliation_failed", context.exception.reasons)
        self.assertIn(
            f"children_sum_reconciliation_missing:{dataset['view']['root_node_id']}",
            context.exception.reasons,
        )

    def test_fontes_exigem_https_dominio_oficial_e_termos_resolvidos(self):
        dataset, report, catalog, approval = fixture()
        catalog["artifacts"][0]["url"] = "http://example.org/mapa"
        catalog["artifacts"][0]["reuse_terms"] = "unresolved"
        with self.assertRaises(MODULE.PublicationError) as context:
            MODULE.validate_gate(dataset, report, catalog, approval)
        self.assertIn("source_not_official_https:mapa-pdf", context.exception.reasons)
        self.assertIn("reuse_terms_unresolved:mapa-pdf", context.exception.reasons)

    def test_aprovacao_humana_tem_de_existir_e_corresponder_ao_sha(self):
        dataset, report, catalog, approval = fixture()
        with self.assertRaises(MODULE.PublicationError) as missing:
            MODULE.validate_gate(dataset, report, catalog, None)
        self.assertIn("human_approval_missing", missing.exception.reasons)
        changed = deepcopy(approval)
        changed["dataset_sha256"] = "0" * 64
        with self.assertRaises(MODULE.PublicationError) as mismatch:
            MODULE.validate_gate(dataset, report, catalog, changed)
        self.assertIn("human_approval_sha256_mismatch", mismatch.exception.reasons)

    def test_aprovacao_exige_identidade_textual_e_data_iso8601(self):
        dataset, report, catalog, approval = fixture()
        for invalid_approved_by in (42, "", "   "):
            with self.subTest(approved_by=invalid_approved_by):
                changed = deepcopy(approval)
                changed["approved_by"] = invalid_approved_by
                with self.assertRaises(MODULE.PublicationError) as context:
                    MODULE.validate_gate(dataset, report, catalog, changed)
                self.assertIn("human_approval_approved_by_invalid", context.exception.reasons)

        for invalid_approved_at in (42, "", "ontem", "2026-02-30T20:00:00Z"):
            with self.subTest(approved_at=invalid_approved_at):
                changed = deepcopy(approval)
                changed["approved_at"] = invalid_approved_at
                with self.assertRaises(MODULE.PublicationError) as context:
                    MODULE.validate_gate(dataset, report, catalog, changed)
                self.assertIn("human_approval_approved_at_invalid", context.exception.reasons)

    def test_falha_nao_escreve_outputs(self):
        dataset, report, catalog, approval = fixture()
        approval["decision"] = "rejected"
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            paths = write_fixture(directory, dataset, report, catalog, approval)
            output = directory / "out"
            with self.assertRaises(MODULE.PublicationError):
                MODULE.prepare(**{f"{name}_path": path for name, path in paths.items()}, output_root=output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

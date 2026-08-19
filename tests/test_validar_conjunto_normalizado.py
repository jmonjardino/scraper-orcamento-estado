import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validar_conjunto_normalizado", ROOT / "ferramentas" / "validar_conjunto_normalizado.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def source(raw_value: str):
    return {
        "source_id": "mapa1", "source_sha256": "a" * 64, "locator": "/Mapa1/x", "raw_value": raw_value,
        "raw_unit": "EUR", "transformation": "EUR decimal × 100 -> integer cents", "kind": "reported",
    }


def dataset():
    root_id = "release:view:root"
    return {
        "release": {"release_id": "release", "year": 2026, "phase": "approved_initial", "publication": "Lei", "dataset_status": "normalized_not_validated"},
        "view": {
            "view_id": "view", "dimension": "programmatic", "root_node_id": root_id,
            "publication_blockers": ["reuse_terms_unresolved"],
            "coverage": {"institutional_universe": "administracao_central", "social_security": "excluded", "consolidation": "non_consolidated", "measure": "budgeted_expenditure", "accounting_classification": "mapa", "gross_net": "not_declared_by_source", "currency": "EUR", "unit": "cents"},
            "reference_total": {"amount_cents": 2000, "source": source("20")},
        },
        "nodes": [
            {"node_id": root_id, "official_code": None, "official_code_status": "not_declared_by_source", "official_label": "Total", "amount_cents": 2000, "year": 2026, "dimension": "programmatic", "level": 0, "parent_node_id": None, "sort_order": 0, "is_terminal": False, "source": source("20")},
            {"node_id": "release:view:P-001", "official_code": "P-001", "official_label": "Programa", "amount_cents": 2000, "year": 2026, "dimension": "programmatic", "level": 1, "parent_node_id": root_id, "sort_order": 1, "is_terminal": True, "source": source("20")},
        ],
    }


class NormalizedDatasetValidationTests(unittest.TestCase):
    def test_conjunto_reconciliado_e_validado_mas_publicacao_permanece_bloqueada(self):
        report = MODULE.validate(dataset())
        self.assertEqual(report["validation_status"], "validated")
        self.assertEqual(report["publication_status"], "blocked")
        self.assertTrue(report["critical_rules_passed"])
        self.assertEqual(report["effective_publication_blockers"], ["reuse_terms_unresolved"])
        self.assertEqual(report["financial_reconciliation"][0]["difference_cents"], 0)

    def test_erro_deliberado_num_valor_rejeita_o_conjunto(self):
        broken = deepcopy(dataset())
        broken["nodes"][1]["amount_cents"] = 1999
        report = MODULE.validate(broken)
        self.assertEqual(report["validation_status"], "rejected")
        self.assertIn("provenance_amount", {entry["rule"] for entry in report["errors"]})
        self.assertIn("children_sum", {entry["rule"] for entry in report["errors"]})

    def test_pai_invalido_e_ciclo_sao_rejeitados(self):
        broken = deepcopy(dataset())
        broken["nodes"][1]["parent_node_id"] = broken["nodes"][1]["node_id"]
        report = MODULE.validate(broken)
        rules = {entry["rule"] for entry in report["errors"]}
        self.assertIn("hierarchy_level", rules)
        self.assertIn("acyclic_hierarchy", rules)

    def test_hash_e_relatorio_sao_deterministas(self):
        first = MODULE.validate(dataset())
        second = MODULE.validate(dataset())
        self.assertEqual(MODULE.canonical_json(first), MODULE.canonical_json(second))


if __name__ == "__main__":
    unittest.main()

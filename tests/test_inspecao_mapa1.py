import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("inspecionar_mapa1", ROOT / "ferramentas" / "inspecionar_mapa1.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Mapa1InspectionTests(unittest.TestCase):
    def test_relatorio_descreve_campos_e_soma_sem_normalizar(self):
        xml = """<Mapa1><Cabecalho><Ano>2026</Ano><UnidadeMonetaria>EUROS</UnidadeMonetaria></Cabecalho><Registos><Registo><Programa>P-001</Programa><DesignacaoPrograma>Programa A</DesignacaoPrograma><Ministério>Ministério A</Ministério><TotalEmEuros>12.50</TotalEmEuros></Registo><Registo><Programa>P-002</Programa><DesignacaoPrograma>Programa B</DesignacaoPrograma><Ministério>Ministério B</Ministério><TotalEmEuros>7.50</TotalEmEuros></Registo></Registos></Mapa1>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapa1.xml"
            path.write_text(xml, encoding="utf-8")
            report = MODULE.inspect(path)
        self.assertEqual(report["record_count"], 2)
        self.assertEqual(report["sum_total_euros"], "20.00")
        self.assertFalse(report["has_explicit_mission_field"])
        self.assertEqual(report["required_fields_missing"], [])

    def test_validacao_aceita_soma_e_campos_da_candidata(self):
        report = {
            "header": {"Ano": "2026", "NumeroMapa": "1"},
            "required_fields_missing": [],
            "record_count": 20,
            "distinct_program_codes": 20,
            "records_with_invalid_total": 0,
            "sum_total_euros": "352472389960",
        }
        catalog = {
            "artifacts": [{
                "source_id": "oe2026-mapa1-xml",
                "reference_total_euros": "352472389960",
                "reference_total_scope": "Administração Central, não consolidado",
                "reference_locator": "Mapa 1, p. 1",
            }]
        }
        validation = MODULE.validate_against_catalog(report, catalog)
        self.assertTrue(all(validation["checks"].values()))
        self.assertEqual(validation["tree_candidate"], "administracao_central_nao_consolidada_por_programa")

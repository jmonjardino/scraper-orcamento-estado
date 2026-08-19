import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("normalizar_mapa1", ROOT / "ferramentas" / "normalizar_mapa1.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Mapa1NormalizationTests(unittest.TestCase):
    def fixture(self, xml: str = None):
        directory = tempfile.TemporaryDirectory()
        archive = Path(directory.name) / "arquivo"
        release_id = "oe-2026-approved-initial"
        source = archive / release_id / "originais" / "mapa1.xml"
        source.parent.mkdir(parents=True)
        xml = xml or """<Mapa1><Cabecalho><Ano>2026</Ano><NumeroMapa>1</NumeroMapa></Cabecalho><Registos><Registo><Programa>P-001</Programa><DesignacaoPrograma>Programa A</DesignacaoPrograma><Ministério>Ministério A</Ministério><TotalEmEuros>12.50</TotalEmEuros></Registo><Registo><Programa>P-002</Programa><DesignacaoPrograma>Programa B</DesignacaoPrograma><Ministério>Ministério B</Ministério><TotalEmEuros>7.50</TotalEmEuros></Registo></Registos></Mapa1>"""
        source.write_text(xml, encoding="utf-8")
        digest = MODULE.hashlib.sha256(source.read_bytes()).hexdigest()
        pdf_source = archive / release_id / "originais" / "mapa1.pdf"
        pdf_source.write_bytes(b"%PDF-1.7\nreferencia")
        pdf_digest = MODULE.hashlib.sha256(pdf_source.read_bytes()).hexdigest()
        manifest = {"release_id": release_id, "year": 2026, "phase": "approved_initial", "artifacts": [
            {"source_id": "oe2026-mapa1-xml", "sha256": digest, "storage_path": "originais/mapa1.xml"},
            {"source_id": "oe2026-mapa1-pdf", "sha256": pdf_digest, "storage_path": "originais/mapa1.pdf"},
        ]}
        catalog = {"release": {"release_id": release_id, "year": 2026, "phase": "approved_initial", "publication": "Lei"}, "artifacts": [{
            "source_id": "oe2026-mapa1-xml", "reference_total_euros": "20", "reference_locator": "Mapa 1, p. 1"
        }]}
        return directory, archive, manifest, catalog

    def test_normaliza_cada_programa_com_cents_pai_e_proveniencia(self):
        directory, archive, manifest, catalog = self.fixture()
        with directory:
            dataset = MODULE.normalize(manifest, catalog, archive)
        root, first, second = dataset["nodes"]
        self.assertEqual(root["amount_cents"], 2000)
        self.assertIsNone(root["official_code"])
        self.assertEqual(first["official_code"], "P-001")
        self.assertEqual(first["amount_cents"], 1250)
        self.assertEqual(first["parent_node_id"], root["node_id"])
        self.assertEqual(first["source"]["source_id"], "oe2026-mapa1-xml")
        self.assertEqual(second["source_attributes"]["ministerio"], "Ministério B")
        self.assertFalse(dataset["view"]["publication_eligible"])

    def test_resultado_e_determinista_e_indice_pesquisa_por_codigo(self):
        directory, archive, manifest, catalog = self.fixture()
        with directory:
            first = MODULE.normalize(manifest, catalog, archive)
            second = MODULE.normalize(manifest, catalog, archive)
        self.assertEqual(MODULE.canonical_json(first), MODULE.canonical_json(second))
        self.assertEqual([entry["official_code"] for entry in first["search_index"]], ["P-001", "P-002"])

    def test_rejeita_valor_sem_precisao_de_centimo(self):
        self.assertRaises(MODULE.NormalizationError, MODULE.euros_to_cents, "1.001")

    def test_rejeita_codigo_repetido(self):
        xml = """<Mapa1><Cabecalho><Ano>2026</Ano><NumeroMapa>1</NumeroMapa></Cabecalho><Registos><Registo><Programa>P-001</Programa><DesignacaoPrograma>A</DesignacaoPrograma><Ministério>M</Ministério><TotalEmEuros>10</TotalEmEuros></Registo><Registo><Programa>P-001</Programa><DesignacaoPrograma>B</DesignacaoPrograma><Ministério>M</Ministério><TotalEmEuros>10</TotalEmEuros></Registo></Registos></Mapa1>"""
        directory, archive, manifest, catalog = self.fixture(xml)
        with directory:
            with self.assertRaises(MODULE.NormalizationError):
                MODULE.normalize(manifest, catalog, archive)

    def test_rejeita_original_que_nao_corresponde_ao_manifesto(self):
        directory, archive, manifest, catalog = self.fixture()
        with directory:
            manifest["artifacts"][0]["sha256"] = "0" * 64
            with self.assertRaises(MODULE.NormalizationError):
                MODULE.normalize(manifest, catalog, archive)


if __name__ == "__main__":
    unittest.main()

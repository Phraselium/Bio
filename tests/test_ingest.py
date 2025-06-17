from src.ingest import ingest

def test_ingest():
    assert ingest('file.pdf') == 'Ingested file.pdf'

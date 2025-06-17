from src.index import build_index

def test_build_index():
    assert build_index([1,2,3]) == 'Index built for 3 items'

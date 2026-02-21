from app.datastructures import HashTable


def test_hashtable_put_get():
    ht = HashTable[str, int](capacity=11)
    ht.put("a", 1)
    ht.put("b", 2)
    assert ht.get("a") == 1
    assert ht.get("b") == 2
    assert ht.get("c") is None


def test_hashtable_remove():
    ht = HashTable[str, int](capacity=11)
    ht.put("x", 9)
    assert ht.contains("x") is True
    assert ht.remove("x") is True
    assert ht.contains("x") is False
    assert ht.remove("x") is False

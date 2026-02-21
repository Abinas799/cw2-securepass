from app.strength import score_password


def test_strength_weak():
    rep = score_password("1234", common_hit=True)
    assert rep.score <= 40
    assert rep.label in ("Weak", "Medium")


def test_strength_strongish():
    rep = score_password("A9!zK2@pQ7#x", common_hit=False)
    assert rep.score >= 50

from app.utils import clamp_int


def test_clamp_int():
    assert clamp_int(5, 6, 64) == 6
    assert clamp_int(100, 6, 64) == 64
    assert clamp_int(12, 6, 64) == 12

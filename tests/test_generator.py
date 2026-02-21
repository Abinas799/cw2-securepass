from app.models import PasswordPolicy
from app.generator import generate_password


def test_generate_password_length():
    policy = PasswordPolicy(
        length=16,
        use_lower=True,
        use_upper=True,
        use_digits=True,
        use_symbols=True,
        exclude_ambiguous=True,
        require_each_selected=True,
    )
    pw = generate_password(policy)
    assert len(pw) == 16

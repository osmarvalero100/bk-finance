import pytest

from app.utils.auth import get_password_hash, verify_password


def test_truncate_long_ascii_password():
    # contraseña ASCII muy larga (>72 bytes)
    pw = 'a' * 200
    hashed = get_password_hash(pw)
    assert isinstance(hashed, str)
    assert verify_password(pw, hashed) is True


def test_truncate_long_multibyte_password():
    # contraseña con caracteres multibyte (emoji) que excede 72 bytes
    pw = '😊' * 40  # cada emoji ocupa varios bytes en UTF-8
    hashed = get_password_hash(pw)
    assert isinstance(hashed, str)
    # La verificación debe ser consistente (se aplica el mismo truncado)
    assert verify_password(pw, hashed) is True


def test_get_password_hash_none_raises():
    with pytest.raises(ValueError):
        get_password_hash(None)

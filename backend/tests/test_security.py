from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hash_roundtrip():
    h = hash_password("secret123")
    assert h != "secret123"
    assert verify_password("secret123", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    token = create_access_token(42, extra={"username": "demo"})
    data = decode_access_token(token)
    assert data is not None
    assert data["sub"] == "42"
    assert data["username"] == "demo"

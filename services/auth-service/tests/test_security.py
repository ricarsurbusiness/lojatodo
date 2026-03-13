import pytest
from app.core.security import verify_password, get_password_hash


def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True


def test_password_verification_wrong():
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password("wrongpassword", hashed) is False


def test_password_hash_uniqueness():
    password = "testpassword123"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    assert hash1 != hash2
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True

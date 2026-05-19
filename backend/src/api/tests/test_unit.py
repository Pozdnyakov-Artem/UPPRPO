import pytest
from datetime import datetime, timedelta
from auth import create_access_token, decode_token_for_cache, verify_password, get_password_hash
from schemas import PinCreate, BoardCreate

def test_password_hashing():
    password = "MySecurePass123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPass", hashed) is False


def test_create_access_token():
    data = {"sub": "testuser", "role": "user"}
    token = create_access_token(data, expires_delta=timedelta(minutes=30))

    assert isinstance(token, str)
    assert len(token) > 100

    decoded = decode_token_for_cache(token)
    assert decoded["sub"] == "testuser"
    assert decoded["role"] == "user"
    assert "exp" in decoded


def test_pin_create_valid():
    pin = PinCreate(
        title="My Pin",
        image_url="https://example.com/img.jpg",
        board_id=1
    )
    assert pin.title == "My Pin"
    assert pin.description is None


def test_pin_create_title_too_long():
    with pytest.raises(ValueError):
        PinCreate(
            title="A" * 201,
            image_url="https://...",
            board_id=1
        )


def test_board_create_minimal():
    board = BoardCreate(name="My Board")
    assert board.name == "My Board"
    assert board.is_private is False
    assert board.description is None
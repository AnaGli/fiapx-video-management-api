import pytest
from app.core.validators import (
    validate_and_normalize_cpf_cnpj,
    validate_and_normalize_plate,
)


def test_valid_cpf():
    assert validate_and_normalize_cpf_cnpj("529.982.247-25") == "52998224725"


def test_invalid_cpf():
    with pytest.raises(ValueError):
        validate_and_normalize_cpf_cnpj("111.111.111-11")


def test_valid_cnpj():
    assert validate_and_normalize_cpf_cnpj("04.252.011/0001-10") == "04252011000110"


def test_valid_plate_old():
    assert validate_and_normalize_plate("abc1234") == "ABC1234"


def test_valid_plate_mercosul():
    assert validate_and_normalize_plate("abc1d23") == "ABC1D23"


def test_invalid_plate():
    with pytest.raises(ValueError):
        validate_and_normalize_plate("123")

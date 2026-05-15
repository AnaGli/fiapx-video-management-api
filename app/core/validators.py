import re


PLATE_OLD_PATTERN = re.compile(r"^[A-Z]{3}[0-9]{4}$")
PLATE_MERCOSUL_PATTERN = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")

def validate_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for i in range(9, 11):
        total = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digit = (total * 10) % 11
        digit = 0 if digit == 10 else digit

        if digit != int(cpf[i]):
            return False

    return True


def validate_cnpj(cnpj: str) -> bool:
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_second = [6] + weights_first

    for i, weights in enumerate([weights_first, weights_second]):
        total = sum(int(cnpj[num]) * weights[num] for num in range(len(weights)))
        digit = 11 - (total % 11)
        digit = 0 if digit >= 10 else digit

        if digit != int(cnpj[12 + i]):
            return False

    return True


def normalize_cpf_cnpj(value: str) -> str:
    return re.sub(r"\D", "", value)


def validate_and_normalize_cpf_cnpj(value: str) -> str:
    digits = normalize_cpf_cnpj(value)

    if len(digits) == 11:
        if not validate_cpf(digits):
            raise ValueError("CPF inválido")
    elif len(digits) == 14:
        if not validate_cnpj(digits):
            raise ValueError("CNPJ inválido")
    else:
        raise ValueError("CPF/CNPJ deve ter 11 ou 14 dígitos")

    return digits

def validate_and_normalize_plate(value: str) -> str:
    if not value:
        raise ValueError("Placa inválida")

    plate = value.strip().upper()

    if PLATE_OLD_PATTERN.match(plate):
        return plate

    if PLATE_MERCOSUL_PATTERN.match(plate):
        return plate

    raise ValueError("Placa inválida")
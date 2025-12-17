# Importamos tus números para poder comparar
from config.settings import MY_NUMBERS


def calculate_match(numbers_sorteo):
    """Calcula cuántos números has acertado."""
    return len(MY_NUMBERS.intersection(numbers_sorteo))


def set_prize(matches, bonus_match, reintegro_match):
    """Determina el tipo de premio según aciertos."""
    if matches == 6 and reintegro_match:
        return "Especial (6 + R)"
    elif matches == 6:
        return "1ª (6 Aciertos)"
    elif matches == 5 and bonus_match:
        return "2ª (5 + C)"
    elif matches == 5:
        return "3ª (5 Aciertos)"
    elif matches == 4:
        return "4ª (4 Aciertos)"
    elif matches == 3:
        return "5ª (3 Aciertos)"
    elif reintegro_match:
        return "Reintegro"
    else:
        return "Sin premio"
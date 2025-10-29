import re
from dataclasses import dataclass
from models.exceptions import ValidationError

@dataclass
class Fecha:

    def __init__(self, text):
        self.valor = self.extraer_fecha(text)

    def extraer_fecha(self, text):
        patron = r'\b\d{2}/\d{2}/\d{4}\b'
        coincidencias = re.findall(patron, text)
        if coincidencias:
            return coincidencias[0]
        else:
            raise ValidationError(f"Sin coincidencias en fecha '{text}'.")

    def __str__(self):
        return self.valor



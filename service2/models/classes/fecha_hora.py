import re
from dataclasses import dataclass
from models.exceptions import ValidationError

@dataclass
class FechaHora:

    def __init__(self, text):
        self.valor = self.extraer_fecha_hora(text)

    def extraer_fecha_hora(self, text):
        patron = r'\b\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\b'
        coincidencias = re.findall(patron, text)
        if coincidencias:
            return coincidencias[0]
        else:
            raise ValidationError(f"Sin coincidencias en fecha y hora '{text}'.")

    def __str__(self):
        return self.valor


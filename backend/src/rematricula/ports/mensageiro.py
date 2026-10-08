from typing import Protocol

from rematricula.domain.telefone import Telefone


class MensageiroWhatsApp(Protocol):
    """Entrega o codigo pelo WhatsApp. Separado da geracao para que o servico de OTP
    possa ser testado sem tocar na Twilio."""

    def enviar_codigo(self, telefone: Telefone, codigo: str) -> None: ...

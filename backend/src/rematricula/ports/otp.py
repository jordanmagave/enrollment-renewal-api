from typing import Protocol

from rematricula.domain.telefone import Telefone


class ServicoOtp(Protocol):
    """Envio e conferencia do codigo de verificacao (Twilio Verify via WhatsApp)."""

    def enviar(self, telefone: Telefone) -> None: ...

    def verificar(self, telefone: Telefone, codigo: str) -> bool: ...

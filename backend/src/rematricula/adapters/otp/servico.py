from dataclasses import dataclass, field

from rematricula.adapters.otp.codigo_derivado import CodigoDerivado
from rematricula.domain.telefone import Telefone
from rematricula.ports.mensageiro import MensageiroWhatsApp


@dataclass(frozen=True, slots=True)
class ServicoOtpWhatsApp:
    """Implementa ServicoOtp: gera o codigo derivado e o entrega pelo WhatsApp.

    Reenviar dentro da mesma janela repete o codigo, entao a mensagem que o
    responsavel ja recebeu continua valendo.
    """

    codigos: CodigoDerivado = field(repr=False)
    mensageiro: MensageiroWhatsApp

    def enviar(self, telefone: Telefone) -> None:
        self.mensageiro.enviar_codigo(telefone, self.codigos.gerar(telefone.e164))

    def verificar(self, telefone: Telefone, codigo: str) -> bool:
        return self.codigos.conferir(telefone.e164, codigo)

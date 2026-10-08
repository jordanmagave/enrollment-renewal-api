import hashlib
import hmac
from datetime import UTC, datetime

_SEGREDO_MINIMO = 32


class CodigoDerivado:
    """Codigo OTP derivado por HMAC do telefone + janela de tempo.

    Nao guarda nada: o mesmo codigo e recalculado na conferencia, como no TOTP.
    A janela anterior tambem e aceita, senao quem recebe a mensagem nos ultimos
    segundos da janela digitaria um codigo ja vencido.

    Atencao: isto resolve a geracao, nao o bloqueio de forca bruta. Seis digitos
    sao um milhao de combinacoes — o limite de tentativas (porta ContadorTentativas)
    e o que impede varrer o espaco.
    """

    def __init__(self, segredo: str, digitos: int, validade_minutos: int) -> None:
        if len(segredo) < _SEGREDO_MINIMO:
            raise ValueError(f"Segredo do OTP precisa de ao menos {_SEGREDO_MINIMO} bytes")

        self._segredo = segredo.encode()
        self._digitos = digitos
        self._janela_segundos = validade_minutos * 60

    def _janela(self, agora: datetime) -> int:
        return int(agora.timestamp()) // self._janela_segundos

    def _para_janela(self, telefone: str, janela: int) -> str:
        assinatura = hmac.new(
            self._segredo, f"{telefone}:{janela}".encode(), hashlib.sha256
        ).digest()
        numero = int.from_bytes(assinatura[:8], "big") % (10**self._digitos)
        return str(numero).zfill(self._digitos)

    def gerar(self, telefone: str, agora: datetime | None = None) -> str:
        momento = agora or datetime.now(UTC)
        return self._para_janela(telefone, self._janela(momento))

    def conferir(self, telefone: str, codigo: str, agora: datetime | None = None) -> bool:
        if len(codigo) != self._digitos or not codigo.isdigit():
            return False

        momento = agora or datetime.now(UTC)
        janela = self._janela(momento)

        return any(
            hmac.compare_digest(self._para_janela(telefone, j), codigo)
            for j in (janela, janela - 1)
        )

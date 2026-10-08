from typing import Protocol


class ContadorTentativas(Protocol):
    """Contagem compartilhada entre instancias. E o que impede varrer as 10^6
    combinacoes do codigo — o codigo em si e derivado e nao guarda estado."""

    def registrar(self, chave: str) -> int:
        """Incrementa e devolve o total de tentativas da chave."""
        ...

    def zerar(self, chave: str) -> None: ...

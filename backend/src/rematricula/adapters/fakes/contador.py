from collections import defaultdict


class ContadorEmMemoria:
    """Contador para testes e desenvolvimento local.

    Nao serve para producao com mais de uma instancia no Cloud Run: cada processo
    teria a sua propria contagem, e o atacante so precisaria cair em outra instancia.
    """

    def __init__(self) -> None:
        self._contagens: dict[str, int] = defaultdict(int)

    def registrar(self, chave: str) -> int:
        self._contagens[chave] += 1
        return self._contagens[chave]

    def zerar(self, chave: str) -> None:
        self._contagens.pop(chave, None)

    def chaves(self) -> list[str]:
        return list(self._contagens)

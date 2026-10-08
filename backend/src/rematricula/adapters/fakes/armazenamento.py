from io import BytesIO

from rematricula.domain.modelos import Servico
from rematricula.ports.armazenamento import BoletoPdf


class ArmazenamentoEmMemoria:
    def __init__(self) -> None:
        self._arquivos: dict[tuple[Servico, str], tuple[str, bytes]] = {}

    def adicionar(
        self, servico: Servico, matricula: str, nome_arquivo: str, conteudo: bytes
    ) -> None:
        self._arquivos[(servico, matricula)] = (nome_arquivo, conteudo)

    def abrir(self, servico: Servico, matricula: str) -> BoletoPdf | None:
        arquivo = self._arquivos.get((servico, matricula))
        if arquivo is None:
            return None

        nome, conteudo = arquivo
        return BoletoPdf(nome_arquivo=nome, conteudo=BytesIO(conteudo))

    def existe(self, servico: Servico, matricula: str) -> bool:
        return (servico, matricula) in self._arquivos

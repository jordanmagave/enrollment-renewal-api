from dataclasses import dataclass

from rematricula.domain.erros import AlunoNaoAutorizado, BoletoIndisponivel
from rematricula.domain.modelos import Servico, Sessao
from rematricula.ports.armazenamento import ArmazenamentoBoletos, BoletoPdf


@dataclass(frozen=True, slots=True)
class BaixarBoleto:
    armazenamento: ArmazenamentoBoletos

    def executar(self, sessao: Sessao, matricula: str, servico: Servico) -> BoletoPdf:
        if not sessao.autoriza(matricula):
            raise AlunoNaoAutorizado("Esse aluno nao esta vinculado ao seu CPF")

        boleto = self.armazenamento.abrir(servico, matricula)
        if boleto is None:
            raise BoletoIndisponivel("Boleto ainda nao disponivel")

        return boleto

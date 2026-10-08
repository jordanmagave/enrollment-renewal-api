from dataclasses import dataclass

from rematricula.domain.cpf import Cpf
from rematricula.domain.erros import CodigoInvalido, TentativasExcedidas
from rematricula.domain.modelos import SessaoEmitida
from rematricula.ports.contador import ContadorTentativas
from rematricula.ports.otp import ServicoOtp
from rematricula.ports.repositorio import RepositorioMatriculas
from rematricula.ports.sessoes import Sessoes


@dataclass(frozen=True, slots=True)
class VerificarCodigo:
    repositorio: RepositorioMatriculas
    otp: ServicoOtp
    sessoes: Sessoes
    contador: ContadorTentativas
    limite_tentativas: int

    def executar(self, cpf: Cpf, codigo: str) -> SessaoEmitida:
        chave = f"verificacao:{cpf.hash()}"

        # Conta antes de conferir, e conta tambem para CPF inexistente: sem isso
        # da para varrer CPFs de graca, e o codigo de 6 digitos cairia por forca bruta.
        if self.contador.registrar(chave) > self.limite_tentativas:
            raise TentativasExcedidas("Muitas tentativas. Fale com a escola")

        responsavel = self.repositorio.buscar_responsavel_por_cpf(cpf)

        # CPF desconhecido responde igual a codigo errado: a API nao pode revelar
        # quem tem cadastro na escola.
        if responsavel is None or not self.otp.verificar(responsavel.telefone, codigo):
            raise CodigoInvalido("Codigo invalido ou expirado")

        self.contador.zerar(chave)
        alunos = self.repositorio.listar_alunos(responsavel.ids)

        return self.sessoes.emitir(
            responsavel_ids=responsavel.ids,
            cpf_hash=cpf.hash(),
            matriculas=tuple(aluno.matricula for aluno in alunos),
        )

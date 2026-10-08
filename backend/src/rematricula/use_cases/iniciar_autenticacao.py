from dataclasses import dataclass

from rematricula.domain.cpf import Cpf
from rematricula.domain.erros import ResponsavelNaoEncontrado, TentativasExcedidas
from rematricula.domain.telefone import Telefone
from rematricula.ports.contador import ContadorTentativas
from rematricula.ports.otp import ServicoOtp
from rematricula.ports.repositorio import RepositorioMatriculas


@dataclass(frozen=True, slots=True)
class IniciarAutenticacao:
    repositorio: RepositorioMatriculas
    otp: ServicoOtp
    contador: ContadorTentativas
    limite_envios: int

    def executar(self, cpf: Cpf) -> Telefone:
        # Conta antes de saber se o CPF existe: cada mensagem no WhatsApp custa, e
        # sem limite qualquer um dispara envios em massa.
        if self.contador.registrar(f"envio:{cpf.hash()}") > self.limite_envios:
            raise TentativasExcedidas("Muitas tentativas. Aguarde alguns minutos")

        responsavel = self.repositorio.buscar_responsavel_por_cpf(cpf)
        if responsavel is None:
            raise ResponsavelNaoEncontrado("Nao encontramos esse CPF no cadastro")

        self.otp.enviar(responsavel.telefone)
        return responsavel.telefone

from fastapi import APIRouter

from rematricula.api.dependencias import Dependencias
from rematricula.api.schemas import (
    ErroResposta,
    IniciarAutenticacaoPedido,
    IniciarAutenticacaoResposta,
    VerificarCodigoPedido,
    VerificarCodigoResposta,
)
from rematricula.domain.cpf import Cpf
from rematricula.use_cases.iniciar_autenticacao import IniciarAutenticacao
from rematricula.use_cases.verificar_codigo import VerificarCodigo

RESPOSTAS_DE_ERRO: dict[int | str, dict[str, object]] = {
    400: {"model": ErroResposta},
    401: {"model": ErroResposta},
    403: {"model": ErroResposta},
    404: {"model": ErroResposta},
    429: {"model": ErroResposta},
}


def criar_router(dependencias: Dependencias) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["autenticacao"])

    @router.post(
        "/iniciar",
        response_model=IniciarAutenticacaoResposta,
        responses=RESPOSTAS_DE_ERRO,
        summary="Envia o codigo de verificacao para o WhatsApp do responsavel",
    )
    def iniciar(pedido: IniciarAutenticacaoPedido) -> IniciarAutenticacaoResposta:
        caso = IniciarAutenticacao(
            repositorio=dependencias.repositorio,
            otp=dependencias.otp,
            contador=dependencias.contador,
            limite_envios=dependencias.limite_envios,
        )
        telefone = caso.executar(Cpf.de_texto(pedido.cpf))
        return IniciarAutenticacaoResposta(telefone_mascarado=telefone.mascarado())

    @router.post(
        "/verificar",
        response_model=VerificarCodigoResposta,
        responses=RESPOSTAS_DE_ERRO,
        summary="Confere o codigo e abre a sessao do responsavel",
    )
    def verificar(pedido: VerificarCodigoPedido) -> VerificarCodigoResposta:
        caso = VerificarCodigo(
            repositorio=dependencias.repositorio,
            otp=dependencias.otp,
            sessoes=dependencias.sessoes,
            contador=dependencias.contador,
            limite_tentativas=dependencias.limite_tentativas,
        )
        emitido = caso.executar(Cpf.de_texto(pedido.cpf), pedido.codigo)
        return VerificarCodigoResposta(
            access_token=emitido.token, expires_in=emitido.expira_em_segundos
        )

    return router

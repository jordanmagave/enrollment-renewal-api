from collections.abc import Iterator
from typing import IO, Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from rematricula.api.dependencias import Dependencias
from rematricula.api.rotas_auth import RESPOSTAS_DE_ERRO
from rematricula.api.schemas import ListaTitulosResposta, TituloItem
from rematricula.api.seguranca import criar_dependencia_de_sessao
from rematricula.domain.modelos import Servico, Sessao
from rematricula.ports.armazenamento import ArmazenamentoBoletos
from rematricula.use_cases.baixar_boleto import BaixarBoleto
from rematricula.use_cases.listar_titulos import ListarTitulos, ResumoDeTitulos

_PEDACO = 64 * 1024


def _resposta(resumo: ResumoDeTitulos, armazenamento: ArmazenamentoBoletos) -> ListaTitulosResposta:
    return ListaTitulosResposta(
        ano_letivo=resumo.ano_letivo,
        desconto_valido_ate=resumo.desconto_valido_ate,
        dias_restantes=resumo.dias_restantes,
        desconto_vigente=resumo.desconto_vigente,
        total_original=resumo.total_original,
        total_com_desconto=resumo.total_com_desconto,
        economia_total=resumo.economia_total,
        itens=[
            TituloItem(
                matricula=titulo.aluno.matricula,
                nome_aluno=titulo.aluno.nome,
                turma=titulo.aluno.turma,
                valor_original=titulo.valor_original,
                desconto=titulo.desconto,
                valor_com_desconto=titulo.valor_com_desconto,
                boleto_disponivel=armazenamento.existe(titulo.servico, titulo.aluno.matricula),
            )
            for titulo in resumo.titulos
        ],
    )


def _em_pedacos(conteudo: IO[bytes]) -> Iterator[bytes]:
    with conteudo:
        while pedaco := conteudo.read(_PEDACO):
            yield pedaco


def _pdf(nome_arquivo: str, conteudo: IO[bytes]) -> StreamingResponse:
    # RFC 5987: o nome tem espacos e acentos (ex.: "100001-ANA BEATRIZ SOUZA LIMA.pdf").
    return StreamingResponse(
        _em_pedacos(conteudo),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(nome_arquivo)}"},
    )


def criar_router(dependencias: Dependencias) -> APIRouter:
    router = APIRouter(tags=["titulos"])
    SessaoAtual = Annotated[Sessao, Depends(criar_dependencia_de_sessao(dependencias.sessoes))]  # noqa: N806

    listar = ListarTitulos(
        repositorio=dependencias.repositorio,
        campanha=dependencias.campanha,
        relogio=dependencias.relogio,
        ano_letivo=dependencias.ano_letivo_alvo,
    )
    baixar = BaixarBoleto(armazenamento=dependencias.armazenamento)

    @router.get(
        "/matriculas",
        response_model=ListaTitulosResposta,
        responses=RESPOSTAS_DE_ERRO,
        summary="Alunos e valores da matricula de janeiro/2027",
    )
    def listar_matriculas(sessao: SessaoAtual) -> ListaTitulosResposta:
        resumo = listar.executar(sessao.responsavel_ids, Servico.MATRICULA)
        return _resposta(resumo, dependencias.armazenamento)

    @router.get(
        "/material-didatico",
        response_model=ListaTitulosResposta,
        responses=RESPOSTAS_DE_ERRO,
        summary="Alunos e valores do material didatico de janeiro/2027",
    )
    def listar_material(sessao: SessaoAtual) -> ListaTitulosResposta:
        resumo = listar.executar(sessao.responsavel_ids, Servico.MATERIAL_DIDATICO)
        return _resposta(resumo, dependencias.armazenamento)

    @router.get(
        "/matriculas/{matricula}/boleto",
        responses=RESPOSTAS_DE_ERRO,
        response_class=StreamingResponse,
        summary="Baixa o boleto de matricula do aluno",
    )
    def boleto_matricula(matricula: str, sessao: SessaoAtual) -> StreamingResponse:
        boleto = baixar.executar(sessao, matricula, Servico.MATRICULA)
        return _pdf(boleto.nome_arquivo, boleto.conteudo)

    @router.get(
        "/material-didatico/{matricula}/boleto",
        responses=RESPOSTAS_DE_ERRO,
        response_class=StreamingResponse,
        summary="Baixa o boleto de material didatico do aluno",
    )
    def boleto_material(matricula: str, sessao: SessaoAtual) -> StreamingResponse:
        boleto = baixar.executar(sessao, matricula, Servico.MATERIAL_DIDATICO)
        return _pdf(boleto.nome_arquivo, boleto.conteudo)

    return router

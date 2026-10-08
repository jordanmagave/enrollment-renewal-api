from datetime import UTC, datetime, timedelta

import pytest

from rematricula.adapters.sessao.sessoes_jwt import SessoesJwt
from rematricula.domain.erros import SessaoInvalida

SEGREDO = "segredo-de-teste-com-32-bytes-ou-mais-aqui"


def sessoes(expira_em_minutos: int = 30) -> SessoesJwt:
    return SessoesJwt(segredo=SEGREDO, expira_em_minutos=expira_em_minutos)


def test_emitir_e_validar_preserva_os_dados_da_sessao() -> None:
    emitido = sessoes().emitir(
        responsavel_ids=("RESP-1",), cpf_hash="abc123", matriculas=("100001", "100002")
    )

    sessao = sessoes().validar(emitido.token)

    assert sessao.responsavel_ids == ("RESP-1",)
    assert sessao.cpf_hash == "abc123"
    assert sessao.matriculas == ("100001", "100002")
    assert emitido.expira_em_segundos == 30 * 60


def test_token_expirado_e_recusado() -> None:
    ontem = datetime.now(UTC) - timedelta(days=1)
    emitido = sessoes().emitir(
        responsavel_ids=("RESP-1",), cpf_hash="abc123", matriculas=(), agora=ontem
    )

    with pytest.raises(SessaoInvalida):
        sessoes().validar(emitido.token)


def test_token_assinado_com_outro_segredo_e_recusado() -> None:
    outras = SessoesJwt(segredo="outro-segredo-com-32-bytes-ou-mais-aqui", expira_em_minutos=30)
    emitido = outras.emitir(responsavel_ids=("RESP-1",), cpf_hash="abc123", matriculas=())

    with pytest.raises(SessaoInvalida):
        sessoes().validar(emitido.token)


@pytest.mark.parametrize("token", ["", "nao-e-um-jwt", "a.b.c"])
def test_token_malformado_e_recusado(token: str) -> None:
    with pytest.raises(SessaoInvalida):
        sessoes().validar(token)

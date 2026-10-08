from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from rematricula.domain.erros import SessaoInvalida
from rematricula.domain.modelos import Sessao, SessaoEmitida

_ALGORITMO = "HS256"


class SessoesJwt:
    def __init__(self, segredo: str, expira_em_minutos: int) -> None:
        self._segredo = segredo
        self._expira_em_minutos = expira_em_minutos

    def emitir(
        self,
        responsavel_ids: tuple[str, ...],
        cpf_hash: str,
        matriculas: tuple[str, ...],
        agora: datetime | None = None,
    ) -> SessaoEmitida:
        emitido_em = agora or datetime.now(UTC)
        expira_em = emitido_em + timedelta(minutes=self._expira_em_minutos)

        payload: dict[str, Any] = {
            "sub": cpf_hash,
            "resp_ids": list(responsavel_ids),
            "matriculas": list(matriculas),
            "iat": int(emitido_em.timestamp()),
            "exp": int(expira_em.timestamp()),
        }
        token = jwt.encode(payload, self._segredo, algorithm=_ALGORITMO)

        return SessaoEmitida(token=token, expira_em_segundos=self._expira_em_minutos * 60)

    def validar(self, token: str) -> Sessao:
        try:
            payload = jwt.decode(token, self._segredo, algorithms=[_ALGORITMO])
        except jwt.PyJWTError as erro:
            raise SessaoInvalida("Sessao invalida ou expirada") from erro

        return Sessao(
            responsavel_ids=tuple(payload["resp_ids"]),
            cpf_hash=str(payload["sub"]),
            matriculas=tuple(payload["matriculas"]),
        )

from fastapi.testclient import TestClient

from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.repositorio import RepositorioEmMemoria
from rematricula.api.dependencias import Dependencias
from rematricula.api.main import criar_app


def test_health_responde_ok() -> None:
    app = criar_app(Dependencias.para_teste(repositorio=RepositorioEmMemoria(), otp=OtpFake()))
    cliente = TestClient(app)

    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}

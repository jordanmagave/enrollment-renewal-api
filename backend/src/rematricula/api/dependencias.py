from dataclasses import dataclass
from datetime import date

from rematricula.adapters.fakes.armazenamento import ArmazenamentoEmMemoria
from rematricula.adapters.fakes.contador import ContadorEmMemoria
from rematricula.adapters.fakes.dados_demo import CODIGO_DEMO, armazenamento_demo, repositorio_demo
from rematricula.adapters.fakes.otp import OtpFake
from rematricula.adapters.fakes.relogio import RelogioFixo
from rematricula.adapters.relogio import RelogioDoSistema
from rematricula.adapters.sessao.sessoes_jwt import SessoesJwt
from rematricula.config import Config
from rematricula.domain.campanha import Campanha
from rematricula.ports.armazenamento import ArmazenamentoBoletos
from rematricula.ports.contador import ContadorTentativas
from rematricula.ports.otp import ServicoOtp
from rematricula.ports.relogio import Relogio
from rematricula.ports.repositorio import RepositorioMatriculas
from rematricula.ports.sessoes import Sessoes

SEGREDO_DE_TESTE = "segredo-de-teste-com-32-bytes-ou-mais-aqui"

# Neste extrato publico os adapters de integracao (banco de leitura, armazenamento
# de PDFs, contador distribuido e envio por WhatsApp) nao estao incluidos: eles
# carregam o schema e a infraestrutura de um cliente. As portas e os fakes estao
# todos aqui, entao a API sobe e a suite roda sem credencial nenhuma.
#
# A forma da raiz de composicao foi preservada de proposito: cada integracao e
# decidida pela sua propria variavel de ambiente, de modo que da para ligar uma
# de cada vez. Com a variavel presente, o metodo falha dizendo o que falta, em
# vez de fingir que o adapter existe.
_AUSENTE = (
    "O adapter concreto de {0} nao faz parte deste extrato publico. "
    "Deixe {1} vazio para subir com o fake de demonstracao."
)


@dataclass(frozen=True, slots=True)
class Dependencias:
    """Raiz de composicao: quem monta os adapters concretos e entrega as portas."""

    repositorio: RepositorioMatriculas
    otp: ServicoOtp
    sessoes: Sessoes
    armazenamento: ArmazenamentoBoletos
    contador: ContadorTentativas
    relogio: Relogio
    campanha: Campanha
    ano_letivo_alvo: int
    limite_envios: int
    limite_tentativas: int
    link_waba: str

    @classmethod
    def de_config(cls, config: Config) -> "Dependencias":
        return cls(
            repositorio=cls._repositorio(config),
            otp=cls._otp(config),
            armazenamento=cls._armazenamento(config),
            contador=cls._contador(config),
            sessoes=SessoesJwt(
                segredo=config.jwt_secret, expira_em_minutos=config.jwt_expira_minutos
            ),
            relogio=RelogioDoSistema(),
            campanha=Campanha(desconto_valido_ate=config.desconto_valido_ate),
            ano_letivo_alvo=config.ano_letivo_alvo,
            limite_envios=config.otp_max_envios,
            limite_tentativas=config.otp_max_tentativas,
            link_waba=config.link_waba,
        )

    @staticmethod
    def _otp(config: Config) -> ServicoOtp:
        pronto = (
            config.twilio_account_sid
            and config.twilio_auth_token
            and config.twilio_whatsapp_number
            and config.twilio_content_sid_otp
            and config.otp_segredo
        )
        if not pronto:
            return OtpFake(codigo_correto=CODIGO_DEMO)
        raise NotImplementedError(_AUSENTE.format("envio de OTP por WhatsApp", "TWILIO_*"))

    @staticmethod
    def _contador(config: Config) -> ContadorTentativas:
        # Sem projeto configurado cai no contador em memoria, que so serve para
        # desenvolvimento: com varias instancias em producao ele nao segura nada.
        if not config.gcp_project:
            return ContadorEmMemoria()
        raise NotImplementedError(
            _AUSENTE.format("contagem distribuida de tentativas", "GCP_PROJECT")
        )

    @staticmethod
    def _repositorio(config: Config) -> RepositorioMatriculas:
        if not (config.motherduck_token and config.motherduck_database):
            return repositorio_demo()
        raise NotImplementedError(_AUSENTE.format("leitura do sistema de gestao", "MOTHERDUCK_*"))

    @staticmethod
    def _armazenamento(config: Config) -> ArmazenamentoBoletos:
        if not config.gcs_bucket_boletos:
            return armazenamento_demo()
        raise NotImplementedError(_AUSENTE.format("armazenamento dos PDFs", "GCS_BUCKET_BOLETOS"))

    @classmethod
    def para_teste(
        cls,
        repositorio: RepositorioMatriculas,
        otp: ServicoOtp,
        armazenamento: ArmazenamentoBoletos | None = None,
        link_waba: str = "",
        desconto_valido_ate: date = date(2027, 1, 31),
        ano_letivo_alvo: int = 2027,
        hoje: date = date(2026, 9, 9),
        limite_envios: int = 100,
        limite_tentativas: int = 100,
    ) -> "Dependencias":
        return cls(
            repositorio=repositorio,
            otp=otp,
            sessoes=SessoesJwt(segredo=SEGREDO_DE_TESTE, expira_em_minutos=30),
            armazenamento=armazenamento or ArmazenamentoEmMemoria(),
            contador=ContadorEmMemoria(),
            relogio=RelogioFixo(hoje),
            campanha=Campanha(desconto_valido_ate=desconto_valido_ate),
            ano_letivo_alvo=ano_letivo_alvo,
            limite_envios=limite_envios,
            limite_tentativas=limite_tentativas,
            link_waba=link_waba,
        )

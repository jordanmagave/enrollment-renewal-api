class ErroDeDominio(Exception):
    """Base de todos os erros de regra de negocio."""


class CpfInvalido(ErroDeDominio):
    pass


class TelefoneInvalido(ErroDeDominio):
    pass


class ResponsavelNaoEncontrado(ErroDeDominio):
    pass


class CodigoInvalido(ErroDeDominio):
    pass


class TentativasExcedidas(ErroDeDominio):
    """Limite de codigos errados ou de envios estourado."""


class SessaoInvalida(ErroDeDominio):
    """Token ausente, adulterado ou expirado."""


class AlunoNaoAutorizado(ErroDeDominio):
    """Matricula pedida nao pertence ao responsavel da sessao."""


class BoletoIndisponivel(ErroDeDominio):
    pass

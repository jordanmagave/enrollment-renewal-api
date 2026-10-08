from datetime import date
from typing import Protocol


class Relogio(Protocol):
    """Injetado para que a contagem regressiva da campanha seja testavel."""

    def hoje(self) -> date: ...

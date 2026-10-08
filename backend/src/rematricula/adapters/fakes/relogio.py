from datetime import date


class RelogioFixo:
    def __init__(self, hoje: date) -> None:
        self._hoje = hoje

    def hoje(self) -> date:
        return self._hoje

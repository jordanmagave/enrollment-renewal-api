# CLAUDE.md

## O que e este projeto

Backend REST de um fluxo de rematricula escolar. O responsavel se autentica com CPF +
codigo enviado por WhatsApp, ve os alunos sob sua responsabilidade com os titulos do ano
letivo alvo e baixa os boletos.

Este repositorio e um extrato publico: os adapters de integracao com sistemas de um
cliente nao estao incluidos. Ver o README.

## Comandos

```bash
cd backend
uv sync
./scripts/check.sh         # ruff -> ruff format -> mypy --strict -> pytest
uv run pytest -q
uv run uvicorn rematricula.api.main:montar_app --factory --app-dir src --reload
```

O `--app-dir src` nao e decorativo: o editable install do `uv` pode nao entrar no
`sys.path`, entao pytest e uvicorn importam direto da arvore de fontes. Sem a flag, o
uvicorn falha com `ModuleNotFoundError: No module named 'rematricula'`.

## Convencoes

- **TDD sem excecao:** teste primeiro (vermelho), codigo depois (verde), `./scripts/check.sh`, commit.
- **Arquitetura hexagonal:** `domain` -> `ports` -> `use_cases` -> `adapters` -> `api`.
  Todo I/O externo entra por uma porta (`Protocol`) e tem um fake em memoria. Caso de uso
  nunca importa adapter.
- **Nada de segredo no codigo.** Sempre `os.getenv()` / settings. `.env` e gitignored.
- **PII fora dos logs.** CPF so como hash + 3 ultimos digitos; telefone sempre mascarado
  nas respostas; log grava template de rota, nunca o caminho concreto.
- **SQL sempre parametrizado.** Nunca f-string em query.
- Codigo, nomes de variaveis e mensagens de dominio em portugues; termos tecnicos em
  ingles quando for o padrao da linguagem.

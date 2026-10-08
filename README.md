# Enrollment Renewal API
[![CI](https://github.com/jordanmagave/enrollment-renewal-api/actions/workflows/ci.yml/badge.svg)](https://github.com/jordanmagave/enrollment-renewal-api/actions/workflows/ci.yml)

A REST backend for a school enrollment-renewal payment flow. A parent or guardian
authenticates with a national ID number plus a one-time code delivered over WhatsApp,
sees the children they are responsible for with the amounts due for the next school
year, and downloads each payment slip without leaving the page.

**This repository is a public extract of a private production system.** The code here
runs, is fully typed and fully tested; what is missing is deliberate. See
[What is not here, and why](#what-is-not-here-and-why).

```bash
cd backend
cp .env.example .env
uv sync
./scripts/check.sh    # ruff -> ruff format -> mypy --strict -> pytest
uv run uvicorn rematricula.api.main:montar_app --factory --app-dir src --reload
```

The API starts with no credentials at all, serving in-memory fakes. Interactive docs at
`http://127.0.0.1:8000/docs`. Demo ID `529.982.247-25`, demo code `123456`.

A note on language: domain code, identifiers and error messages are in Portuguese,
because the business language of the project is Portuguese and the domain terms have no
clean English equivalents. Technical terms follow the convention of the language. The
architecture should be legible regardless: `domain` → `ports` → `use_cases` → `adapters`
→ `api`.

---

## Privacy is a design constraint, not a checklist item

This system handles national ID numbers, phone numbers, children's names and payment
data. Three decisions carry most of the weight.

**A national ID cannot be printed by accident.** `Cpf` is a frozen value object whose
`__repr__` returns the masked form. There is no code path, including a stack trace or a
careless debug statement, that emits the full number. A stable SHA-256 hash is available
for log correlation and as a JWT subject claim, so you can follow one person through a
request without ever storing who they are.

```python
@dataclass(frozen=True, slots=True, repr=False)
class Cpf:
    digitos: str

    def mascarado(self) -> str:
        return f"***.***.{self.digitos[6:9]}-{self.digitos[9:]}"

    def hash(self) -> str:
        """Identificador estavel para log e claim de JWT, sem expor o CPF."""
        return hashlib.sha256(self.digitos.encode()).hexdigest()
```

**The request log records the route template, never the path.** The enrollment number in
a URL identifies a specific child, so the middleware substitutes each path parameter
back to its name before logging. Body, query string and headers are never logged at all,
because every one of them carries an ID, a phone number or a token.

**That rule is enforced by a test, not by discipline.** `test_log.py` asserts that an
enrollment number does not appear anywhere in the logger output. A privacy rule with no
test is an intention.

---

## Architecture

Hexagonal, and the reason is testability rather than taste. Every piece of external I/O
enters through a `Protocol` in `ports/`, and **every port has an in-memory fake**. That is
what makes it possible to develop and test the whole system without a single credential,
and it is why the suite runs in about a second.

```
backend/src/rematricula/
├── domain/      # pure rules: ID validation, phone normalisation, campaign deadline
├── ports/       # Protocols: repository, OTP service, slip storage,
│                # attempt counter, messenger, sessions, clock
├── use_cases/   # start_authentication, verify_code, list_charges, download_slip
├── adapters/    # fakes/ (all ports), otp/ (derived codes), sessao/ (JWT), relogio/
└── api/         # composition root, routes, schemas, security, logging
```

A use case never imports an adapter. The composition root in `api/dependencias.py`
decides each integration by its own environment variable, so integrations can be switched
on one at a time rather than all or nothing.

### Security choices worth naming

- **One-time codes are derived, not stored.** `adapters/otp/codigo_derivado.py` computes
  the code from a secret plus the identity and a time window, so there is no table of
  live codes to leak. The OTP secret is separate from the JWT secret: leaking one does
  not compromise the other.
- **Rate limiting is the actual control.** A six-digit code is brute-forceable in
  seconds, so per-identity limits on both attempts and resends are what make it safe.
  `test_limite_de_tentativas.py` is the longest test file in the repository for that
  reason.
- **JWT secrets are length-checked at startup.** A short key weakens HS256; RFC 7518
  asks for at least 32 bytes, and the config refuses to start below that.
- **SQL is always parameterised.** No f-strings in queries, enforced by review and by
  `ruff`'s `S` rules.

---

## Tests

99 tests, all green with no credentials and no network:

```
ruff check .          # E, F, I, N, UP, B, S, C4, SIM, RUF
ruff format --check .
mypy --strict         # 44 source files, no ignores outside third-party stubs
pytest -q             # 99 passed
```

CI runs exactly the same four steps on every push and pull request, and `scripts/check.sh`
mirrors CI so the feedback is identical locally.

The private original has 127 tests plus 4 contract tests that run only against real
credentials. The difference is the tests for the excluded adapters.

---

## What is not here, and why

The concrete integration adapters are excluded: the read-only repository over the
school-management system's data warehouse, the object-storage adapter for the payment
slips, the distributed attempt counter, and the WhatsApp messenger. So are the schema
documentation and the operational wiki.

Those files encode a client's database schema, bucket names and cloud project. Publishing
them would expose a third party's infrastructure to demonstrate my own work, which is not
a trade I am willing to make. The ports they implement are all here, the fakes are all
here, and the composition root keeps the shape of the real wiring: with the relevant
environment variable set, each factory raises a `NotImplementedError` naming what is
missing rather than pretending the adapter exists.

The demo fixture data is synthetic. Names, enrollment numbers and amounts were replaced;
the national ID is the canonical Brazilian test value, valid by checksum and belonging to
nobody.

In production this service runs on Cloud Run, with the four real integrations validated
against live services.

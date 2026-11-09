"""Rate limit simples em memória (por processo)."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request

_lock = Lock()
_buckets: dict[str, deque[float]] = defaultdict(deque)


def checar_rate_limit(chave: str, maximo: int, janela_segundos: int = 60) -> None:
    agora = time.monotonic()
    with _lock:
        fila = _buckets[chave]
        while fila and agora - fila[0] > janela_segundos:
            fila.popleft()
        if len(fila) >= maximo:
            raise HTTPException(status_code=429, detail="Muitas tentativas. Aguarde e tente novamente.")
        fila.append(agora)


def chave_cliente(request: Request, sufixo: str) -> str:
    ip = request.client.host if request.client else "desconhecido"
    return f"{ip}:{sufixo}"


def limpar_rate_limits() -> None:
    """Utilitário de testes: zera contadores em memória."""
    with _lock:
        _buckets.clear()

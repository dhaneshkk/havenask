#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shared hardening helpers for the llm/ demo services.

Configuration (environment variables):
  LLM_API_KEY        If set, every API request must send
                     "Authorization: Bearer <key>" or "X-API-Key: <key>".
                     If unset, the server only accepts unauthenticated use when
                     bound to a loopback address (see SERVER_HOST).
  SERVER_HOST        Bind address. Defaults to 127.0.0.1 (was 0.0.0.0).
  MAX_UPLOAD_BYTES   Largest accepted upload for /files. Default 20 MiB.
  MAX_TOPN           Largest accepted Query.topn. Default 50.
"""

import hmac
import logging
import os
import re
from typing import Optional

from fastapi import Header, HTTPException, status

DEFAULT_HOST = '127.0.0.1'
DEFAULT_MAX_UPLOAD_BYTES = 20 * 1024 * 1024
DEFAULT_MAX_TOPN = 50

# Havenask's push-document format separates fields with \x1F and documents with
# \x1E. Any C0 control character other than tab/newline is removed from values
# so user content cannot forge fields or extra documents.
_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b-\x1f\x7f]')
_SAFE_FILENAME_CHARS = re.compile(r'[^A-Za-z0-9._ -]')
_LOOPBACK_HOSTS = {'127.0.0.1', 'localhost', '::1'}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == '':
        return default
    try:
        value = int(raw)
    except ValueError:
        raise RuntimeError(f'{name} must be an integer, got {raw!r}')
    if value <= 0:
        raise RuntimeError(f'{name} must be positive, got {value}')
    return value


def server_host() -> str:
    return os.environ.get('SERVER_HOST') or DEFAULT_HOST


def max_upload_bytes() -> int:
    return _env_int('MAX_UPLOAD_BYTES', DEFAULT_MAX_UPLOAD_BYTES)


def max_topn() -> int:
    return _env_int('MAX_TOPN', DEFAULT_MAX_TOPN)


def strip_control_chars(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return _CONTROL_CHARS.sub('', value)


def sanitize_filename(name: Optional[str], fallback: str = 'upload') -> str:
    """Reduce a client-supplied file name to a safe, bounded basename."""
    if not name:
        return fallback
    # Normalise Windows separators first so "..\\x" cannot survive basename().
    base = os.path.basename(name.replace('\\', '/'))
    base = _SAFE_FILENAME_CHARS.sub('_', base).strip(' .')
    return base[:200] or fallback


def check_startup_config() -> None:
    """Refuse to start an unauthenticated server on a non-loopback address."""
    host = server_host()
    if os.environ.get('LLM_API_KEY'):
        return
    if host in _LOOPBACK_HOSTS:
        logging.warning('LLM_API_KEY is not set: API is unauthenticated (bound to %s only).', host)
        return
    raise RuntimeError(
        f'Refusing to serve without authentication on {host}. '
        'Set LLM_API_KEY, or bind to 127.0.0.1 via SERVER_HOST.')


async def require_api_key(authorization: Optional[str] = Header(default=None),
                          x_api_key: Optional[str] = Header(default=None)) -> None:
    """FastAPI dependency enforcing LLM_API_KEY when it is configured."""
    expected = os.environ.get('LLM_API_KEY')
    if not expected:
        return
    supplied = x_api_key
    if supplied is None and authorization and authorization.lower().startswith('bearer '):
        supplied = authorization[len('bearer '):].strip()
    if supplied is None or not hmac.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='invalid or missing API key',
                            headers={'WWW-Authenticate': 'Bearer'})

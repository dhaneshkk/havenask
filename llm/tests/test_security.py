import asyncio

import pytest
from fastapi import HTTPException

from util import security


@pytest.mark.parametrize('raw, expected', [
    ('plain text', 'plain text'),
    ('keeps\ttab\nand newline', 'keeps\ttab\nand newline'),
    ('a\x1Fb\x1Ec', 'abc'),
    ('nul\x00bell\x07del\x7f', 'nulbelldel'),
    (None, None),
])
def test_strip_control_chars(raw, expected):
    assert security.strip_control_chars(raw) == expected


@pytest.mark.parametrize('raw, expected', [
    ('report.pdf', 'report.pdf'),
    ('../../etc/passwd', 'passwd'),
    ('..\\..\\windows\\win.ini', 'win.ini'),
    ('a\x1Eb;rm -rf.md', 'a_b_rm -rf.md'),
    ('', 'upload'),
    (None, 'upload'),
    ('...', 'upload'),
    ('x' * 500 + '.txt', 'x' * 200),
])
def test_sanitize_filename(raw, expected):
    assert security.sanitize_filename(raw) == expected


def _call(**headers):
    return asyncio.run(security.require_api_key(**headers))


def test_api_key_not_required_when_unset(monkeypatch):
    monkeypatch.delenv('LLM_API_KEY', raising=False)
    assert _call(authorization=None, x_api_key=None) is None


@pytest.mark.parametrize('headers', [
    dict(authorization=None, x_api_key=None),
    dict(authorization='Bearer wrong', x_api_key=None),
    dict(authorization='Basic s3cret', x_api_key=None),
    dict(authorization=None, x_api_key='s3cre'),
])
def test_api_key_rejected(monkeypatch, headers):
    monkeypatch.setenv('LLM_API_KEY', 's3cret')
    with pytest.raises(HTTPException) as exc:
        _call(**headers)
    assert exc.value.status_code == 401


@pytest.mark.parametrize('headers', [
    dict(authorization='Bearer s3cret', x_api_key=None),
    dict(authorization='bearer s3cret', x_api_key=None),
    dict(authorization=None, x_api_key='s3cret'),
])
def test_api_key_accepted(monkeypatch, headers):
    monkeypatch.setenv('LLM_API_KEY', 's3cret')
    assert _call(**headers) is None


def test_startup_refuses_public_bind_without_key(monkeypatch):
    monkeypatch.delenv('LLM_API_KEY', raising=False)
    monkeypatch.setenv('SERVER_HOST', '0.0.0.0')
    with pytest.raises(RuntimeError):
        security.check_startup_config()


def test_startup_allows_loopback_or_key(monkeypatch):
    monkeypatch.delenv('LLM_API_KEY', raising=False)
    monkeypatch.delenv('SERVER_HOST', raising=False)
    security.check_startup_config()  # default 127.0.0.1
    monkeypatch.setenv('SERVER_HOST', '0.0.0.0')
    monkeypatch.setenv('LLM_API_KEY', 'k')
    security.check_startup_config()


def test_env_int_validation(monkeypatch):
    monkeypatch.setenv('MAX_UPLOAD_BYTES', 'lots')
    with pytest.raises(RuntimeError):
        security.max_upload_bytes()
    monkeypatch.setenv('MAX_UPLOAD_BYTES', '0')
    with pytest.raises(RuntimeError):
        security.max_upload_bytes()
    monkeypatch.setenv('MAX_UPLOAD_BYTES', '10')
    assert security.max_upload_bytes() == 10

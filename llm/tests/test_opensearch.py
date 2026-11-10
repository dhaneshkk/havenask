import asyncio
import json
import types

import pytest

from vectorstore import aliyun_opensearch


class _FakeClient:
    def __init__(self, body=None, exc=None):
        self._body, self._exc = body, exc

    def __call__(self, config):  # used as client.Client(config)
        return self

    async def search_async(self, request):
        if self._exc:
            raise self._exc
        return types.SimpleNamespace(body=self._body)


def _query(monkeypatch, fake):
    monkeypatch.setattr(aliyun_opensearch.client, 'Client', fake)
    return asyncio.run(aliyun_opensearch.AliyunOpenSearch().query([0.1, 0.2], 3))


def test_returns_rows(monkeypatch):
    body = json.dumps({'error_info': {'ErrorCode': 0},
                       'sql_result': {'data': [['p1', 'c1', 's1']]}})
    rows = _query(monkeypatch, _FakeClient(body=body))
    assert [(r.pk, r.content, r.source_id) for r in rows] == [('p1', 'c1', 's1')]


def test_engine_error_is_raised_not_swallowed(monkeypatch):
    body = json.dumps({'error_info': {'ErrorCode': 7, 'Message': 'boom'}})
    with pytest.raises(RuntimeError, match='boom'):
        _query(monkeypatch, _FakeClient(body=body))


def test_transport_error_is_raised_not_swallowed(monkeypatch):
    with pytest.raises(ConnectionError):
        _query(monkeypatch, _FakeClient(exc=ConnectionError('down')))

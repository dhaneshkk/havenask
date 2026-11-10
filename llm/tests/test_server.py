import os
import sys

import pytest
from fastapi.testclient import TestClient

# The store the stubbed factory (tests/conftest.py) hands to the server.
FAKE_STORE = sys.modules['vectorstore.factory'].get_vector_store()

KEY = 'test-key'
AUTH = {'Authorization': f'Bearer {KEY}'}


class FakeSpliter:
    async def split_token_with_overlap(self, text):
        return [text[i:i + 10] for i in range(0, len(text), 10)] if text else []


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('LLM_API_KEY', KEY)
    monkeypatch.delenv('SERVER_HOST', raising=False)
    monkeypatch.setenv('MAX_UPLOAD_BYTES', '64')  # tiny, so the limit test stays fast
    from server import server
    monkeypatch.setattr(server, 'SentenceSpliter', FakeSpliter)
    FAKE_STORE.inserted.clear()
    FAKE_STORE.queries.clear()
    with TestClient(server.app) as c:
        yield c


@pytest.mark.parametrize('method, path, kwargs', [
    ('post', '/chat', dict(json={'query': 'hi'})),
    ('post', '/stream-chat', dict(json={'query': 'hi'})),
    ('post', '/documents', dict(json={'documents': []})),
    ('post', '/files', dict(files={'file': ('a.txt', b'x')})),
])
def test_every_route_requires_key(client, method, path, kwargs):
    assert getattr(client, method)(path, **kwargs).status_code == 401
    bad = {'Authorization': 'Bearer nope'}
    assert getattr(client, method)(path, headers=bad, **kwargs).status_code == 401


def test_chat_with_key(client):
    r = client.post('/chat', json={'query': 'hi', 'topn': 2}, headers=AUTH)
    assert r.status_code == 200
    assert r.json()['result'] == 'answer to hi'
    assert FAKE_STORE.queries == [2]


def test_chat_rejects_unbounded_topn(client):
    r = client.post('/chat', json={'query': 'hi', 'topn': 100000}, headers=AUTH)
    assert r.status_code == 422
    assert FAKE_STORE.queries == []


def test_upload_size_limit(client):
    r = client.post('/files', files={'file': ('big.txt', b'a' * 65)}, headers=AUTH)
    assert r.status_code == 413
    assert FAKE_STORE.inserted == []


def test_upload_unsupported_type_is_400(client):
    r = client.post('/files', files={'file': ('x.exe', b'MZ')}, headers=AUTH)
    assert r.status_code == 400


def test_upload_filename_is_sanitized(client):
    r = client.post('/files', files={'file': ('../../etc/no;tes$(id).txt', b'line one\nline two\n')}, headers=AUTH)
    assert r.status_code == 200
    assert FAKE_STORE.inserted, 'document should have been stored'
    assert {d.source_id for d in FAKE_STORE.inserted} == {'no_tes__id_.txt'}


def test_upload_temp_files_are_removed(client, tmp_path, monkeypatch):
    import tempfile
    monkeypatch.setattr(tempfile, 'tempdir', str(tmp_path))
    client.post('/files', files={'file': ('a.txt', b'abc')}, headers=AUTH)
    client.post('/files', files={'file': ('b.exe', b'abc')}, headers=AUTH)  # error path
    assert os.listdir(tmp_path) == []


def test_startup_refuses_public_unauthenticated(monkeypatch):
    monkeypatch.delenv('LLM_API_KEY', raising=False)
    monkeypatch.setenv('SERVER_HOST', '0.0.0.0')
    from server import server
    with pytest.raises(RuntimeError):
        with TestClient(server.app):
            pass

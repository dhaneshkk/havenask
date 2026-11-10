"""Test setup: put llm/ on sys.path and stub the heavy/remote dependencies.

The server's real adapters pull in torch, transformers, openai and the Alibaba
Cloud SDK. None of that is needed to test request handling, so lightweight
fakes are installed in sys.modules before anything under test is imported.
"""
import os
import sys
import types

LLM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LLM_DIR not in sys.path:
    sys.path.insert(0, LLM_DIR)


class FakeLLM:
    """Stands in for llm_adapter.openai.OpenAI / chatglm.ChatGLM."""

    @classmethod
    async def embed_text(cls, text):
        return [0.1, 0.2, 0.3]

    @classmethod
    async def embed_query(cls, text):
        return [0.1, 0.2, 0.3]

    @classmethod
    async def chat(cls, contexts, query, history, **kwargs):
        return f'answer to {query}', history + [[query, 'answer']]


class FakeStore:
    def __init__(self):
        self.inserted = []
        self.queries = []

    async def insert(self, docs):
        self.inserted.extend(docs)

    async def query(self, embedding, topn):
        from models.models import HAResult
        self.queries.append(topn)
        return [HAResult(pk='doc_0', content='ctx', source_id='doc')]


FAKE_STORE = FakeStore()


def _install(name, **attrs):
    module = types.ModuleType(name)
    module.__dict__.update(attrs)
    sys.modules[name] = module
    return module


_install('llm_adapter.factory', get_llm_adapter=lambda: FakeLLM)
_install('vectorstore.factory', get_vector_store=lambda: FAKE_STORE)

# Alibaba Cloud SDK used by vectorstore/aliyun_opensearch.py.
_ha3 = _install('alibabacloud_ha3engine')
_ha3.models = _install('alibabacloud_ha3engine.models',
                       Config=lambda **kw: kw,
                       SearchQuery=lambda **kw: kw,
                       SearchRequestModel=lambda *a: a,
                       PushDocumentsRequestModel=lambda *a: a)
_ha3.client = _install('alibabacloud_ha3engine.client', Client=None)
_install('Tea')
_install('Tea.exceptions', TeaException=Exception, RetryError=Exception)

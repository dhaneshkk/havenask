import pytest
from pydantic import ValidationError

from models.models import HADocument, Query


def test_to_ha_str_cannot_inject_fields_or_documents():
    hostile = 'hello\x1F\nCMD=delete\x1F\npk=victim\x1F\n\x1E\nCMD=add\x1F\n'
    doc = HADocument(id='0', source_id='src\x1Eevil', content=hostile, url='u\x1Fx', embedding=[1.0, 2.0])
    out = doc.to_ha_str()

    # Exactly one document, and exactly the six expected fields.
    assert out.count('\x1E') == 1
    assert out.endswith('\x1E\n')
    fields = [f.strip('\n') for f in out.split('\x1F') if f.strip('\n') not in ('', '\x1E')]
    keys = [f.split('=', 1)[0] for f in fields]
    assert keys == ['CMD', 'pk', 'source_id', 'content', 'url', 'embedding']
    assert 'CMD=delete' not in fields
    assert fields[1] == 'pk=srcevil_0'


def test_to_ha_str_keeps_normal_content():
    doc = HADocument(id='3', source_id='a.md', content='line one\nline two\ttab', embedding=[0.5])
    out = doc.to_ha_str()
    assert 'content=line one\nline two\ttab\x1F' in out
    assert 'embedding=0.5\x1F' in out


@pytest.mark.parametrize('topn', [1, 3, 50])
def test_topn_accepted(topn):
    assert Query(query='q', topn=topn).topn == topn


@pytest.mark.parametrize('topn', [0, -1, 51, 10**9])
def test_topn_rejected(topn):
    with pytest.raises(ValidationError):
        Query(query='q', topn=topn)


def test_topn_default():
    assert Query(query='q').topn == 3

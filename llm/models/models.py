#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Optional, Any
from pydantic import BaseModel, validator
from util.security import max_topn, strip_control_chars

class Document(BaseModel):
    id: str
    content: str
    url: Optional[str] = None

class DocumentList(BaseModel):
    documents: List[Document]

class Query(BaseModel):
    query: str
    history: Optional[List[Any]] = []
    topn: Optional[int] = 3

    @validator('topn')
    def _bound_topn(cls, v):
        # Unbounded topn let a single request ask the vector index for any n.
        if v is None:
            return 3
        limit = max_topn()
        if not 1 <= v <= limit:
            raise ValueError(f'topn must be between 1 and {limit}')
        return v

class HAResult(BaseModel):
    pk: str
    content: str
    source_id: str

class HADocument(BaseModel):
    id: str
    source_id: str
    content: str
    url: Optional[str] = None
    embedding: List[float]

    @property
    def pk(self):
        return self.source_id + '_' + self.id

    def to_ha_str(self) -> str:
        # Values are written into Havenask's \x1F/\x1E-delimited push format;
        # strip control characters so content cannot inject fields or documents.
        clean = strip_control_chars
        doc_str = 'CMD=add\x1F\n'
        doc_str += f'pk={clean(self.pk)}\x1F\n'
        doc_str += f'source_id={clean(self.source_id)}\x1F\n'
        doc_str += f'content={clean(self.content)}\x1F\n'
        if self.url is not None:
            doc_str += f'url={clean(self.url)}\x1F\n'
        doc_str += f'embedding={",".join([str(p) for p in self.embedding])}\x1F\n'
        doc_str += '\x1E\n'
        return doc_str

    def to_os_doc(self):
        fields = {
            'pk': self.pk,
            'source_id': self.source_id,
            'content': self.content,
            'url': self.url,
            'embedding': self.embedding
        }
        doc = {
            'cmd': 'add',
            'fields': fields
        }
        return doc

class InsertResponse(BaseModel):
    success: bool

class QueryResponse(BaseModel):
    success: bool
    result: str
    history: List[Any]
    source: List[str]
    finished: Optional[bool] = True

class QueryStreamResponse(BaseModel):
    success: bool
    result: str
    finished: bool

class  ChunkConfig(BaseModel):
    max_count: int
    size: int
    overlap: int
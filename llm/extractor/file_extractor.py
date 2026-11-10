import os
import tempfile
from PyPDF2 import PdfReader
from fastapi import HTTPException, UploadFile, status
from .markdown_extractor import MarkdownExtractor

_READ_CHUNK = 1024 * 1024


async def read_limited(file: UploadFile, max_bytes: int) -> bytes:
    """Read an upload, rejecting it with 413 as soon as it exceeds max_bytes."""
    data = bytearray()
    while True:
        chunk = await file.read(_READ_CHUNK)
        if not chunk:
            return bytes(data)
        data += chunk
        if len(data) > max_bytes:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                detail=f'upload exceeds {max_bytes} bytes')


async def extract_file(file: UploadFile, file_name: str, max_bytes: int):
    fs = await read_limited(file, max_bytes)
    # A private per-request temp file. The previous fixed path (/tmp/temp_file)
    # was shared by concurrent uploads, so one request could parse another's
    # data, and it was open to symlink tricks in a shared /tmp.
    fd, temp_file_path = tempfile.mkstemp(prefix='havenask_llm_upload_')
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(fs)
        return extract_file_content(temp_file_path, file_name)
    except (HTTPException, ValueError):
        raise
    except Exception as e:
        print(f'extract file[{file_name}], error[{str(e)}]')
        raise
    finally:
        os.remove(temp_file_path)


def extract_file_content(file_path: str, file_name: str):
    lower = file_name.lower()
    if lower.endswith('.pdf'):
        reader = PdfReader(file_path)
        extracted_text = " ".join([page.extract_text() or '' for page in reader.pages])
    elif lower.endswith('.txt') or lower.endswith('.md'):
        with open(file_path, encoding='utf-8', errors='replace') as fd:
            content = fd.read()
            extracted_text = MarkdownExtractor().extract(content)
    else:
        raise ValueError(f'unsupported file type, file name: {file_name}')
    return extracted_text

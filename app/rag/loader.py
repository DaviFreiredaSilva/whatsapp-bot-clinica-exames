import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def load_documents(docs_dir: str) -> list:
    path = Path(docs_dir)
    if not path.exists():
        logger.warning("docs_dir '%s' não encontrado.", docs_dir)
        return []

    raw_docs = []

    for pdf_file in path.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        raw_docs.extend(loader.load())
        logger.info("PDF carregado: %s", pdf_file.name)

    for txt_file in path.glob("*.txt"):
        loader = TextLoader(str(txt_file), encoding="utf-8")
        raw_docs.extend(loader.load())
        logger.info("TXT carregado: %s", txt_file.name)

    if not raw_docs:
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(raw_docs)
    logger.info("%d chunks gerados a partir de %d documento(s).", len(chunks), len(raw_docs))
    return chunks

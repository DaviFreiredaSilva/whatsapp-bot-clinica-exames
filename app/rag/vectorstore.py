import logging

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.rag.loader import load_documents

logger = logging.getLogger(__name__)

_retriever = None


async def init_rag():
    global _retriever

    docs = load_documents(settings.docs_dir)
    if not docs:
        logger.warning("Nenhum documento encontrado em '%s' — RAG desativado.", settings.docs_dir)
        return

    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
    _retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    logger.info("RAG inicializado com %d chunks.", len(docs))


def get_retriever():
    return _retriever

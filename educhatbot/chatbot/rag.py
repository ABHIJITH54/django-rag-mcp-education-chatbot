from pathlib import Path
from uuid import uuid4

import chromadb
from chromadb.utils import embedding_functions
from django.conf import settings
from pypdf import PdfReader

from learning.models import StudyMaterial


COLLECTION_NAME = "education_materials"


def get_collection():
    settings.CHATBOT_CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(settings.CHATBOT_CHROMA_DIR))
    embedder = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedder,
        metadata={"hnsw:space": "cosine"},
    )


def extract_pdf_text(file_path):
    reader = PdfReader(file_path)
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((index, text.strip()))
    return pages


def chunk_text(text, chunk_size=900, overlap=150):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start >= len(text) or end >= len(text):
            break
    return chunks


def index_material(material_id):
    material = StudyMaterial.objects.select_related("course").get(id=material_id)
    file_path = Path(material.file.path)

    if file_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF indexing is implemented in this demo.")

    collection = get_collection()
    ids = []
    documents = []
    metadatas = []

    for page_number, page_text in extract_pdf_text(file_path):
        for chunk_index, chunk in enumerate(chunk_text(page_text)):
            ids.append(str(uuid4()))
            documents.append(chunk)
            metadatas.append(
                {
                    "material_id": material.id,
                    "material_title": material.title,
                    "course_id": material.course_id,
                    "course_title": material.course.title,
                    "page": page_number,
                    "chunk": chunk_index,
                }
            )

    if documents:
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    return len(documents)


def search_documents(question, course_id=None, limit=5):
    collection = get_collection()
    where = {"course_id": course_id} if course_id else None
    result = collection.query(
        query_texts=[question],
        n_results=limit,
        where=where,
    )

    matches = []
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    for document, metadata in zip(documents, metadatas):
        matches.append({"text": document, "metadata": metadata})

    return matches

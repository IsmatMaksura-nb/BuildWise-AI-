

from pathlib import Path
from typing import List, Dict, Any
import hashlib

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


# =====================================================================
# 1. PATH CONFIGURATION
# =====================================================================

BASE_DIR = Path(__file__).resolve().parents[1]

CHROMA_DIR = BASE_DIR / "database" / "chroma_db"

COLLECTION_NAME = "buildwise_documents"


# =====================================================================
# 2. EMBEDDING MODEL
# =====================================================================

# Multilingual model:
# Supports English and Bangla text.
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


_embeddings = None


def get_embeddings():
    """
    Creates the embedding model only when needed.

    The model is downloaded automatically on first use
    and then kept in memory for subsequent requests.
    """

    global _embeddings

    if _embeddings is None:

        print(
            "[BuildWise-RAG] "
            "Initializing embedding model..."
        )

        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        print(
            "[BuildWise-RAG] "
            "Embedding model initialized successfully."
        )

    return _embeddings


# =====================================================================
# 3. CHROMA DATABASE
# =====================================================================

def get_vectorstore():
    """
    Returns the persistent ChromaDB vector store.
    """

    CHROMA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_DIR)
    )

    return vectorstore


# =====================================================================
# 4. TEXT CHUNKING
# =====================================================================

def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> List[str]:
    """
    Splits long document text into smaller overlapping chunks.

    Chunking is important because the entire document should not be
    embedded and retrieved as one huge block.
    """

    if not text or not text.strip():
        return []

    text = text.strip()

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks


# =====================================================================
# 5. DOCUMENT HASH
# =====================================================================

def _create_document_hash(
    text: str,
    source_name: str
) -> str:
    """
    Creates a stable hash for a document.

    The hash is used to detect whether the same document
    has already been stored in ChromaDB.
    """

    normalized_source = (
        source_name or "uploaded_document"
    ).strip().lower()

    content = (
        normalized_source
        + "\n"
        + (text or "").strip()
    )

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


# =====================================================================
# 6. CHECK IF DOCUMENT ALREADY EXISTS
# =====================================================================

def _document_already_exists(
    vectorstore,
    document_hash: str
) -> bool:
    """
    Checks whether a document with the same hash
    is already stored in ChromaDB.
    """

    try:

        collection = vectorstore._collection

        result = collection.get(
            where={
                "document_hash": document_hash
            },
            limit=1
        )

        ids = result.get(
            "ids",
            []
        )

        return bool(ids)

    except Exception as e:

        print(
            "[BuildWise-RAG] "
            f"Duplicate document check failed: {e}"
        )

        # If the check fails, allow normal ingestion
        # instead of blocking the document.
        return False


# =====================================================================
# 7. ADD DOCUMENT TO CHROMADB
# =====================================================================

def add_document_to_rag(
    text: str,
    source_name: str = "uploaded_document",
    metadata: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Chunks extracted document text and stores it in ChromaDB.

    If the same document has already been stored,
    embedding and ingestion are skipped.
    """

    if not text or not text.strip():

        return {
            "success": False,
            "message": "No document text was provided.",
            "chunks_added": 0,
            "already_exists": False
        }

    # ---------------------------------------------------------------
    # Create stable document hash
    # ---------------------------------------------------------------

    document_hash = _create_document_hash(
        text=text,
        source_name=source_name
    )

    # ---------------------------------------------------------------
    # Split document into chunks
    # ---------------------------------------------------------------

    chunks = split_text(text)

    if not chunks:

        return {
            "success": False,
            "message": "Document could not be split into chunks.",
            "chunks_added": 0,
            "already_exists": False
        }

    # ---------------------------------------------------------------
    # Open vector store
    # ---------------------------------------------------------------

    vectorstore = get_vectorstore()

    # ---------------------------------------------------------------
    # Check for duplicate document
    # ---------------------------------------------------------------

    if _document_already_exists(
        vectorstore=vectorstore,
        document_hash=document_hash
    ):

        print(
            "[BuildWise-RAG] "
            f"Document already exists: {source_name}"
        )

        return {
            "success": True,
            "message": "Document already exists in ChromaDB. Skipped re-ingestion.",
            "source": source_name,
            "chunks_added": 0,
            "already_exists": True
        }

    # ---------------------------------------------------------------
    # Prepare metadata
    # ---------------------------------------------------------------

    base_metadata = metadata.copy() if metadata else {}

    documents = []

    for index, chunk in enumerate(chunks):

        chunk_metadata = {
            **base_metadata,
            "source": source_name,
            "chunk_id": index,
            "document_hash": document_hash
        }

        documents.append(
            Document(
                page_content=chunk,
                metadata=chunk_metadata
            )
        )

    # ---------------------------------------------------------------
    # Generate unique IDs
    # ---------------------------------------------------------------

    ids = [
        f"{document_hash}_{i}"
        for i in range(len(documents))
    ]

    # ---------------------------------------------------------------
    # Store documents
    # ---------------------------------------------------------------

    print(
        "[BuildWise-RAG] "
        f"Embedding and storing {len(documents)} chunk(s)..."
    )

    vectorstore.add_documents(
        documents=documents,
        ids=ids
    )

    print(
        "[BuildWise-RAG] "
        "Document successfully stored in ChromaDB."
    )

    return {
        "success": True,
        "message": "Document successfully added to ChromaDB.",
        "source": source_name,
        "chunks_added": len(documents),
        "already_exists": False
    }


# =====================================================================
# 8. RETRIEVE RELEVANT DOCUMENT CHUNKS
# =====================================================================

def retrieve_relevant_chunks(
    query: str,
    k: int = 4
) -> List[Dict[str, Any]]:
    """
    Retrieves the most relevant document chunks from ChromaDB.
    """

    if not query or not query.strip():

        return []

    try:

        vectorstore = get_vectorstore()

        results = vectorstore.similarity_search_with_score(
            query,
            k=k
        )

    except Exception as e:

        print(
            "[BuildWise-RAG] "
            f"Retrieval error: {e}"
        )

        return []

    retrieved = []

    for document, score in results:

        retrieved.append({
            "content": document.page_content,
            "metadata": document.metadata,
            "score": float(score)
        })

    return retrieved


# =====================================================================
# 9. BUILD CONTEXT FOR LLM
# =====================================================================

def get_rag_context(
    query: str,
    k: int = 4
) -> str:
    """
    Retrieves relevant chunks and combines them into an LLM-ready context.
    """

    results = retrieve_relevant_chunks(
        query=query,
        k=k
    )

    if not results:

        return ""

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):

        source = result["metadata"].get(
            "source",
            "Unknown source"
        )

        content = result["content"]

        context_parts.append(
            f"[Retrieved Context {index}]\n"
            f"Source: {source}\n"
            f"{content}"
        )

    return "\n\n".join(context_parts)


# =====================================================================
# 10. SIMPLE DATABASE STATUS
# =====================================================================

def get_rag_status() -> Dict[str, Any]:
    """
    Returns basic ChromaDB status information.
    """

    try:

        vectorstore = get_vectorstore()

        collection = vectorstore._collection

        count = collection.count()

        return {
            "success": True,
            "collection": COLLECTION_NAME,
            "chunks": count,
            "database_path": str(CHROMA_DIR)
        }

    except Exception as e:

        return {
            "success": False,
            "collection": COLLECTION_NAME,
            "chunks": 0,
            "error": str(e)
        }


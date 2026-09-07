

import hashlib
import threading
from pathlib import Path

import pymupdf


# ============================================================
# 1. OCR CACHE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

OCR_CACHE_DIR = BASE_DIR / "database" / "ocr_cache"

OCR_CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def _get_pdf_hash(pdf_bytes: bytes) -> str:
    """
    Creates a unique SHA-256 hash for the uploaded PDF.
    """

    return hashlib.sha256(
        pdf_bytes
    ).hexdigest()


def _get_cache_path(pdf_bytes: bytes) -> Path:
    """
    Returns the cache file path for a PDF.
    """

    pdf_hash = _get_pdf_hash(
        pdf_bytes
    )

    return OCR_CACHE_DIR / f"{pdf_hash}.txt"


def _load_cached_ocr(pdf_bytes: bytes) -> str:
    """
    Loads previously extracted OCR text if available.
    """

    cache_path = _get_cache_path(
        pdf_bytes
    )

    if not cache_path.exists():
        return ""

    try:

        text = cache_path.read_text(
            encoding="utf-8"
        )

        if text.strip():

            print(
                "[BuildWise-OCR] "
                "Cached OCR text found. "
                "Skipping OCR."
            )

            return text

    except Exception as e:

        print(
            "[BuildWise-OCR] "
            f"Could not read OCR cache: {e}"
        )

    return ""


def _save_cached_ocr(
    pdf_bytes: bytes,
    text: str
) -> None:
    """
    Saves OCR text into the local cache.
    """

    if not text or not text.strip():
        return

    cache_path = _get_cache_path(
        pdf_bytes
    )

    try:

        cache_path.write_text(
            text,
            encoding="utf-8"
        )

        print(
            "[BuildWise-OCR] "
            "OCR text cached successfully."
        )

    except Exception as e:

        print(
            "[BuildWise-OCR] "
            f"Could not save OCR cache: {e}"
        )


# ============================================================
# 2. LAZY-LOADED EASYOCR READER
# ============================================================

_ocr_reader = None
_ocr_lock = threading.Lock()


def _get_ocr_reader():
    """
    Returns a shared EasyOCR Reader instance.
    Lazy-loaded on first call; cached for subsequent calls.
    Supports English ('en') and Bengali ('bn').
    """

    global _ocr_reader

    if _ocr_reader is None:

        with _ocr_lock:

            if _ocr_reader is None:

                import easyocr

                print(
                    "[BuildWise-OCR] "
                    "Initializing EasyOCR reader (en + bn)... "
                    "First run may download models."
                )

                _ocr_reader = easyocr.Reader(
                    ['en', 'bn'],
                    gpu=False,
                    verbose=False
                )

                print(
                    "[BuildWise-OCR] "
                    "EasyOCR reader initialized successfully."
                )

    return _ocr_reader


# ============================================================
# 3. PDF PAGE → IMAGE RENDERING
# ============================================================

def _render_page_to_image_bytes(
    page: pymupdf.Page,
    dpi: int = 200
) -> bytes:
    """
    Renders a single PyMuPDF page to PNG image bytes.

    200 DPI is used for faster OCR processing while
    maintaining good readability for construction drawings.
    """

    zoom = dpi / 72.0

    matrix = pymupdf.Matrix(
        zoom,
        zoom
    )

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False
    )

    return pixmap.tobytes(
        "png"
    )


# ============================================================
# 4. OCR TEXT EXTRACTION
# ============================================================

def extract_text_with_ocr(
    pdf_bytes: bytes
) -> str:
    """
    Extracts text from a scanned/image-based PDF using EasyOCR.

    Process:
    1. Checks OCR cache.
    2. Opens PDF using PyMuPDF.
    3. Renders each page at 200 DPI.
    4. Runs EasyOCR.
    5. Saves extracted text to cache.
    """

    try:

        # ----------------------------------------------------
        # CHECK CACHE FIRST
        # ----------------------------------------------------

        cached_text = _load_cached_ocr(
            pdf_bytes
        )

        if cached_text:

            return cached_text

        # ----------------------------------------------------
        # GET OCR READER
        # ----------------------------------------------------

        reader = _get_ocr_reader()

        # ----------------------------------------------------
        # OPEN PDF
        # ----------------------------------------------------

        doc = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        all_page_texts = []

        # ----------------------------------------------------
        # PROCESS PAGES
        # ----------------------------------------------------

        for page_num in range(
            len(doc)
        ):

            page = doc[page_num]

            print(
                f"[BuildWise-OCR] "
                f"Processing page "
                f"{page_num + 1}/{len(doc)} via OCR..."
            )

            # Render page
            image_bytes = (
                _render_page_to_image_bytes(
                    page
                )
            )

            # Run OCR
            results = reader.readtext(
                image_bytes,
                detail=0,
                paragraph=True
            )

            page_text = (
                "\n".join(results)
                if results
                else ""
            )

            if page_text.strip():

                all_page_texts.append(
                    f"--- Page {page_num + 1} ---\n"
                    f"{page_text}"
                )

        # ----------------------------------------------------
        # CLOSE PDF
        # ----------------------------------------------------

        doc.close()

        # ----------------------------------------------------
        # COMBINE TEXT
        # ----------------------------------------------------

        if all_page_texts:

            final_text = "\n\n".join(
                all_page_texts
            )

            # Save OCR result
            _save_cached_ocr(
                pdf_bytes,
                final_text
            )

            return final_text

        return ""

    except Exception as e:

        error_msg = (
            f"[BuildWise-OCR] "
            f"OCR extraction error: {str(e)}"
        )

        print(
            error_msg
        )

        return (
            f"Error during OCR extraction: "
            f"{str(e)}"
        )


# ============================================================
# 5. TEXT QUALITY CHECK
# ============================================================

_JUNK_PATTERNS = [
    "camscanner",
    "scanned by",
    "created by",
    "adobe acrobat",
    "powered by",
    "trial version",
]


def is_text_sufficient(
    text: str,
    min_meaningful_chars: int = 50
) -> bool:
    """
    Checks whether extracted text is meaningful enough
    to skip OCR.
    """

    if not text or not text.strip():

        return False

    cleaned = (
        text.strip().lower()
    )

    # Remove common junk/watermarks
    for junk in _JUNK_PATTERNS:

        cleaned = cleaned.replace(
            junk,
            ""
        )

    # Keep only alphanumeric characters
    meaningful = "".join(
        c
        for c in cleaned
        if c.isalnum()
    )

    return (
        len(meaningful)
        >= min_meaningful_chars
    )
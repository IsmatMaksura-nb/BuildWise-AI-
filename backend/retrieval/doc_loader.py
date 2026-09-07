

from typing import Dict, Any, Optional

import pymupdf

from backend.retrieval.ocr import (
    extract_text_with_ocr,
    is_text_sufficient
)

from backend.tools.rag_tool import (
    add_document_to_rag,
    get_rag_context
)


# ============================================================
# 1. PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF using PyMuPDF.
    """

    try:

        doc = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        text_parts = []

        for page_num in range(len(doc)):

            page = doc[page_num]

            page_text = page.get_text()

            if page_text:

                text_parts.append(
                    page_text
                )

        doc.close()

        return "\n".join(
            text_parts
        )

    except Exception as e:

        return (
            f"Error extracting PDF text: "
            f"{str(e)}"
        )


# ============================================================
# 2. SMART PDF EXTRACTION
# ============================================================

def smart_extract_pdf_text(
    pdf_bytes: bytes
) -> tuple:
    """
    First tries PyMuPDF.
    If text is insufficient, uses EasyOCR.

    OCR module automatically checks its cache,
    so repeated uploads of the same PDF skip OCR.
    """

    # --------------------------------------------------------
    # NORMAL PDF TEXT EXTRACTION
    # --------------------------------------------------------

    text = extract_text_from_pdf_bytes(
        pdf_bytes
    )

    if is_text_sufficient(text):

        print(
            "[BuildWise-DocLoader] "
            "Text extraction successful "
            "(text-based PDF)."
        )

        return text, "text"

    # --------------------------------------------------------
    # OCR FALLBACK
    # --------------------------------------------------------

    print(
        "[BuildWise-DocLoader] "
        "Text extraction insufficient, "
        "falling back to OCR..."
    )

    ocr_text = extract_text_with_ocr(
        pdf_bytes
    )

    if (
        ocr_text
        and ocr_text.strip()
        and not ocr_text.startswith("Error")
    ):

        print(
            "[BuildWise-DocLoader] "
            "OCR extraction successful."
        )

        return ocr_text, "ocr"

    # --------------------------------------------------------
    # OCR FAILED
    # --------------------------------------------------------

    print(
        "[BuildWise-DocLoader] "
        "OCR extraction returned no text. "
        "Using original text."
    )

    return text, "text"


# ============================================================
# 3. RAG INGESTION
# ============================================================

def ingest_document_into_rag(
    extracted_text: str,
    doc_name: str
) -> Dict[str, Any]:
    """
    Adds extracted document text to ChromaDB.
    """

    if not extracted_text or not extracted_text.strip():

        return {
            "success": False,
            "message": "No text available for RAG ingestion.",
            "chunks_added": 0
        }

    try:

        result = add_document_to_rag(
            text=extracted_text,
            source_name=doc_name or "uploaded_document",
            metadata={
                "document_type":
                    "construction_document"
            }
        )

        print(
            "[BuildWise-DocLoader] "
            f"RAG ingestion result: {result}"
        )

        return result

    except Exception as e:

        print(
            "[BuildWise-DocLoader] "
            f"RAG ingestion error: {e}"
        )

        return {
            "success": False,
            "message": str(e),
            "chunks_added": 0
        }


# ============================================================
# 4. NORMAL CONSTRUCTION AI FALLBACK
# ============================================================

def _generate_general_construction_answer(
    llm,
    query: str,
    language: str
) -> Optional[str]:

    if llm is None:

        print(
            "[BuildWise-DocLoader] "
            "LLM is None. Cannot generate fallback answer."
        )

        return None

    try:

        from langchain_core.messages import (
            SystemMessage,
            HumanMessage
        )

        system_instruction = """
You are BuildWiseAI, a helpful construction and
civil engineering assistant.

The user may have uploaded a construction document,
but the current question does not have enough relevant
information in that document.

Answer the user's question using your general
construction, civil engineering, architecture,
building planning, and construction knowledge.

IMPORTANT RULES:

1. Do not pretend that the answer came from the uploaded
   document.

2. Do not invent details about the uploaded building.

3. If the question asks for a specific value from the
   uploaded document and that value is unavailable,
   clearly say that it is not specified in the document.

4. For general educational construction questions,
   provide a clear and useful explanation.

5. For engineering calculations, clearly state assumptions.

6. Do not claim that a building is structurally safe or
   code compliant without sufficient evidence.

7. For structural design decisions, recommend verification
   by a qualified civil/structural engineer when appropriate.

8. Keep the answer concise, practical, and easy to understand.

9. Answer in the requested language.
"""

        user_prompt = f"""
Requested Language:
{language}

User Question:
{query}

The uploaded document did not provide sufficiently
relevant information for this particular question.

Please answer the question using general construction
and civil engineering knowledge.

Do NOT present the answer as information extracted
from the uploaded document.
"""

        messages = [
            SystemMessage(
                content=system_instruction
            ),
            HumanMessage(
                content=user_prompt
            )
        ]

        print(
            "[BuildWise-DocLoader] "
            "Generating normal construction AI fallback..."
        )

        response = llm.invoke(
            messages
        )

        if response is None:
            return None

        if not hasattr(
            response,
            "content"
        ):
            return None

        content = response.content

        if isinstance(
            content,
            list
        ):

            try:

                content = "\n".join(
                    str(item)
                    for item in content
                )

            except Exception:

                content = str(
                    content
                )

        else:

            content = str(
                content
            )

        if content.strip():

            print(
                "[BuildWise-DocLoader] "
                "Normal construction AI fallback successful."
            )

            return content.strip()

        return None

    except Exception as e:

        import traceback

        print(
            "\n"
            "============================================================"
        )

        print(
            "[BuildWise-DocLoader] "
            "GENERAL AI FALLBACK ERROR"
        )

        print(
            f"Error Type: {type(e).__name__}"
        )

        print(
            f"Error Message: {str(e)}"
        )

        print(
            "============================================================"
        )

        traceback.print_exc()

        print(
            "============================================================\n"
        )

        return None


# ============================================================
# 5. GROUNDED LLM DOCUMENT ANALYSIS
# ============================================================

def _generate_llm_analysis(
    llm,
    extracted_text: str,
    rag_context: str,
    doc_name: str,
    query: str,
    language: str
) -> Optional[str]:

    if llm is None:

        print(
            "[BuildWise-DocLoader] "
            "LLM is None. Skipping AI analysis."
        )

        return None

    if not rag_context or not rag_context.strip():

        print(
            "[BuildWise-DocLoader] "
            "No relevant RAG context. "
            "Document-grounded analysis skipped."
        )

        return None

    try:

        from langchain_core.messages import (
            SystemMessage,
            HumanMessage
        )

        grounding_instruction = """
You are BuildWiseAI's Document Analysis Agent.

Your job is to answer questions about construction
documents using ONLY the information available in the
retrieved document context.

STRICT RULES:

1. Use only information explicitly present in the
   provided document context.

2. NEVER invent, assume, estimate, or guess missing
   construction or structural information.

3. NEVER add specifications that are not present.

4. Do NOT invent:
   - concrete grades
   - rebar grades
   - concrete mix ratios
   - foundation types
   - column sizes
   - beam sizes
   - slab thickness
   - structural loads
   - reinforcement details
   - material specifications
   - structural dimensions
   - BNBC/ACI/ASTM compliance
   - safety conclusions

5. If the requested information is not available in the
   retrieved context, say:

   "Not specified in the provided document."

6. Retrieved RAG context is evidence extracted from the
   uploaded document.

7. Do not use outside knowledge as if it came from the
   uploaded document.

8. OCR text may contain spelling mistakes, missing
   characters, or incorrect dimensions.

9. If a value appears uncertain because of OCR, write:

   "OCR-uncertain"

   and recommend verification from the original drawing.

10. If giving advice that is not directly present in the
    document, label it:

    "General recommendation"

11. Do not claim that a building is structurally safe,
    unsafe, code compliant, or code non-compliant unless
    the provided document explicitly supports that
    conclusion.

12. Preserve units and dimensions exactly as they appear
    whenever possible.

13. If the document does not contain enough information
    for an engineering conclusion, clearly say so.

14. Keep the final answer clear and organized.
"""

        user_query = (
            query.strip()
            if query and query.strip()
            else "Provide a general analysis of this document."
        )

        analysis_prompt = f"""
DOCUMENT ANALYSIS TASK

Document Name:
{doc_name or "Unknown"}

Requested Language:
{language}

User Query:
{user_query}

============================================================
RETRIEVED DOCUMENT CONTEXT
============================================================

{rag_context}

============================================================
END OF RETRIEVED DOCUMENT CONTEXT
============================================================

Now answer the user's question.

IMPORTANT:

- Use only the retrieved document context above.
- Do not invent missing information.
- If information is missing, say:
  "Not specified in the provided document."
- If OCR appears uncertain, mark it:
  "OCR-uncertain"
- Any advice beyond the document must be labelled:
  "General recommendation".
- Do not claim structural safety or code compliance
  without sufficient evidence.
"""

        messages = [
            SystemMessage(
                content=grounding_instruction
            ),
            HumanMessage(
                content=analysis_prompt
            )
        ]

        print(
            "[BuildWise-DocLoader] "
            "Sending RAG context to Groq LLM..."
        )

        response = llm.invoke(
            messages
        )

        if response is None:

            print(
                "[BuildWise-DocLoader] "
                "LLM returned None."
            )

            return None

        if not hasattr(
            response,
            "content"
        ):

            print(
                "[BuildWise-DocLoader] "
                "LLM response has no content attribute."
            )

            return None

        content = response.content

        if isinstance(
            content,
            list
        ):

            try:

                content = "\n".join(
                    str(item)
                    for item in content
                )

            except Exception:

                content = str(
                    content
                )

        else:

            content = str(
                content
            )

        if content.strip():

            print(
                "[BuildWise-DocLoader] "
                "RAG-grounded LLM analysis successful."
            )

            return content.strip()

        print(
            "[BuildWise-DocLoader] "
            "LLM returned empty content."
        )

        return None

    except Exception as e:

        import traceback

        print(
            "\n"
            "============================================================"
        )

        print(
            "[BuildWise-DocLoader] "
            "LLM ANALYSIS ERROR"
        )

        print(
            f"Error Type: {type(e).__name__}"
        )

        print(
            f"Error Message: {str(e)}"
        )

        print(
            "============================================================"
        )

        traceback.print_exc()

        print(
            "============================================================\n"
        )

        return None


# ============================================================
# 6. MAIN DOCUMENT ANALYSIS FUNCTION
# ============================================================

def analyze_document_content(
    doc_bytes: Optional[bytes] = None,
    doc_name: Optional[str] = None,
    query: str = "",
    is_bangla: bool = False,
    llm=None
) -> Dict[str, Any]:

    extracted_text = ""

    extraction_method = "none"

    rag_result = {
        "success": False,
        "chunks_added": 0
    }

    # ========================================================
    # 1. DOCUMENT EXTRACTION
    # ========================================================

    if doc_bytes and doc_name:

        if doc_name.lower().endswith(
            ".pdf"
        ):

            extracted_text, extraction_method = (
                smart_extract_pdf_text(
                    doc_bytes
                )
            )

        else:

            try:

                extracted_text = doc_bytes.decode(
                    "utf-8",
                    errors="ignore"
                )

                extraction_method = "text"

            except Exception as e:

                print(
                    "[BuildWise-DocLoader] "
                    f"Text file decoding error: {e}"
                )

                extracted_text = ""

                extraction_method = "none"

    # ========================================================
    # 2. INGEST DOCUMENT INTO CHROMADB
    # ========================================================

    if extracted_text and extracted_text.strip():

        rag_result = ingest_document_into_rag(
            extracted_text=extracted_text,
            doc_name=doc_name or "uploaded_document"
        )

    # ========================================================
    # 3. LANGUAGE
    # ========================================================

    language = (
        "Bangla"
        if is_bangla
        else "English"
    )

    # ========================================================
    # 4. RETRIEVE RELEVANT RAG CONTEXT
    # ========================================================

    rag_context = ""

    if query and query.strip():

        try:

            rag_context = get_rag_context(
                query=query,
                k=4
            )

            if rag_context:

                print(
                    "[BuildWise-DocLoader] "
                    "Relevant RAG context retrieved."
                )

            else:

                print(
                    "[BuildWise-DocLoader] "
                    "No relevant RAG context found."
                )

        except Exception as e:

            print(
                "[BuildWise-DocLoader] "
                f"RAG retrieval error: {e}"
            )

    # ========================================================
    # 5. ANSWER GENERATION
    # ========================================================

    llm_analysis = None

    answer_source = "none"

    if rag_context and rag_context.strip():

        llm_analysis = _generate_llm_analysis(
            llm=llm,
            extracted_text=extracted_text,
            rag_context=rag_context,
            doc_name=doc_name or "Unknown",
            query=query,
            language=language
        )

        if llm_analysis:

            answer_source = "document_rag"

    if not llm_analysis:

        print(
            "[BuildWise-DocLoader] "
            "Using normal construction AI fallback."
        )

        llm_analysis = _generate_general_construction_answer(
            llm=llm,
            query=query,
            language=language
        )

        if llm_analysis:

            answer_source = "general_ai"

    # ========================================================
    # 6. EXTRACTION METHOD LABEL
    # ========================================================

    method_label = {

        "text":
            "📝 Standard Text Extraction "
            "(PyMuPDF)",

        "ocr":
            "🔍 OCR Extraction "
            "(EasyOCR — scanned/image PDF detected)",

        "none":
            "⚠️ No text could be extracted"

    }.get(
        extraction_method,
        "Unknown"
    )

    # ========================================================
    # 7. EXTRACTED TEXT SNIPPET
    # ========================================================

    snippet = ""

    if extracted_text:

        snippet = extracted_text[
            :800
        ].strip()

    # ========================================================
    # 8. ANSWER SOURCE LABEL
    # ========================================================

    if answer_source == "document_rag":

        source_label_en = (
            "📚 Answer Source: Uploaded Document + ChromaDB RAG"
        )

        source_label_bn = (
            "📚 উত্তর উৎস: আপলোড করা ডকুমেন্ট + ChromaDB RAG"
        )

    elif answer_source == "general_ai":

        source_label_en = (
            "🤖 Answer Source: General Construction AI "
            "(not found in uploaded document)"
        )

        source_label_bn = (
            "🤖 উত্তর উৎস: সাধারণ Construction AI "
            "(আপলোড করা ডকুমেন্টে তথ্য পাওয়া যায়নি)"
        )

    else:

        source_label_en = (
            "⚠️ Answer Source: None"
        )

        source_label_bn = (
            "⚠️ উত্তর উৎস: কোনো উত্তর উৎস নেই"
        )

    # ========================================================
    # 9. BANGLA REPORT
    # ========================================================

    if is_bangla:

        method_label_bn = {

            "text":
                "📝 সাধারণ টেক্সট এক্সট্রাকশন "
                "(PyMuPDF)",

            "ocr":
                "🔍 OCR এক্সট্রাকশন "
                "(EasyOCR — স্ক্যানড/ইমেজ PDF সনাক্ত)",

            "none":
                "⚠️ কোনো টেক্সট এক্সট্রাক্ট "
                "করা যায়নি"

        }.get(
            extraction_method,
            "অজানা"
        )

        report = (
            "📄 **ডকুমেন্ট বিশ্লেষণ রিপোর্ট "
            "(Document Analyzer)**\n\n"

            f"নথি"
            f"{f' (*{doc_name}*)' if doc_name else ''}"
            f" | প্রশ্ন: "
            f"*\"{query if query else 'নথির সার্বিক বিশ্লেষণ'}\"*"
            f"\n\n"

            f"**এক্সট্রাকশন পদ্ধতি:** "
            f"{method_label_bn}\n\n"

            f"**RAG Status:** "
            f"{'✅ ChromaDB-তে সংরক্ষিত' if rag_result.get('success') else '⚠️ RAG ingestion সম্পন্ন হয়নি'}"
            f"\n\n"

            f"**উত্তর উৎস:** "
            f"{source_label_bn}\n\n"
        )

        if snippet:

            report += (
                "📌 **নথি থেকে প্রাপ্ত তথ্য:**\n"
                f"> {snippet[:700]}\n\n"
            )

        if llm_analysis:

            if answer_source == "document_rag":

                report += (
                    "---\n\n"
                    "🤖 **AI ডকুমেন্ট বিশ্লেষণ:**\n\n"
                    f"{llm_analysis}"
                )

            else:

                report += (
                    "---\n\n"
                    "🤖 **AI উত্তর:**\n\n"
                    f"{llm_analysis}"
                )

        elif not snippet:

            report += (
                "⚠️ নথি থেকে কোনো টেক্সট পাওয়া যায়নি "
                "এবং AI উত্তর তৈরি করা যায়নি।"
            )

        else:

            report += (
                "⚠️ **AI উত্তর তৈরি করা যায়নি।**\n\n"
                "বিস্তারিত error server terminal-এ দেখানো হয়েছে।"
            )

    # ========================================================
    # 10. ENGLISH REPORT
    # ========================================================

    else:

        report = (
            "📄 **Document Analysis Report**\n\n"

            f"Document"
            f"{f' (*{doc_name}*)' if doc_name else ''}"
            f" | Query: "
            f"*\"{query if query else 'General Document Analysis'}\"*"
            f"\n\n"

            f"**Extraction Method:** "
            f"{method_label}\n\n"

            f"**RAG Status:** "
            f"{'✅ Stored in ChromaDB' if rag_result.get('success') else '⚠️ RAG ingestion not completed'}"
            f"\n\n"

            f"**Answer Source:** "
            f"{source_label_en}\n\n"
        )

        if snippet:

            report += (
                "📌 **Extracted Document Information:**\n"
                f"> {snippet[:700]}\n\n"
            )

        if llm_analysis:

            if answer_source == "document_rag":

                report += (
                    "---\n\n"
                    "🤖 **AI Document Analysis:**\n\n"
                    f"{llm_analysis}"
                )

            else:

                report += (
                    "---\n\n"
                    "🤖 **AI Construction Answer:**\n\n"
                    f"{llm_analysis}"
                )

        elif not snippet:

            report += (
                "⚠️ No text could be extracted from "
                "this document and an AI answer could "
                "not be generated."
            )

        else:

            report += (
                "⚠️ **AI answer could not be completed.**\n\n"
                "Please check the server terminal for "
                "the detailed error."
            )

    # ========================================================
    # 11. RETURN RESULT
    # ========================================================

    return {

        "doc_name": doc_name,

        "extracted_length":
            len(extracted_text),

        "extraction_method":
            extraction_method,

        "rag_success":
            rag_result.get(
                "success",
                False
            ),

        "rag_chunks_added":
            rag_result.get(
                "chunks_added",
                0
            ),

        "rag_context_found":
            bool(
                rag_context
            ),

        "answer_source":
            answer_source,

        "formatted_report":
            report
    }


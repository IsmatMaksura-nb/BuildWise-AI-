

from typing import Optional

from backend.retrieval.doc_loader import analyze_document_content


class DocumentAgent:

    def __init__(self, llm=None):
        self.name = "BuildWise Document Agent"
        self.llm = llm

    def process(
        self,
        file_bytes: Optional[bytes],
        file_name: Optional[str],
        user_input: str,
        language: str = "English"
    ) -> str:
        """
        Analyze an uploaded construction document.

        The actual OCR, text extraction, RAG retrieval,
        and grounded LLM analysis are handled by doc_loader.py.
        """

        is_bangla = language.lower() == "bangla"

        # -------------------------------------------------------------
        # Validate document
        # -------------------------------------------------------------

        if not file_bytes:
            if is_bangla:
                return (
                    "📄 **ডকুমেন্ট পাওয়া যায়নি**\n\n"
                    "দয়া করে একটি construction document upload করুন।"
                )

            return (
                "📄 **No document uploaded**\n\n"
                "Please upload a construction document "
                "before starting the analysis."
            )

        # -------------------------------------------------------------
        # Existing OCR + RAG + Grounded Analysis Pipeline
        # -------------------------------------------------------------

        try:

            result = analyze_document_content(
                doc_bytes=file_bytes,
                doc_name=file_name or "uploaded_document",
                query=user_input,
                is_bangla=is_bangla,
                llm=self.llm
            )

            return result["formatted_report"]

        except Exception as e:

            print(f"[DocumentAgent] Error: {e}")

            if is_bangla:
                return (
                    "❌ **ডকুমেন্ট বিশ্লেষণে সমস্যা হয়েছে।**\n\n"
                    "দয়া করে আবার চেষ্টা করুন।"
                )

            return (
                "❌ **Document analysis failed.**\n\n"
                "Please try again with the uploaded document."
            )


# =====================================================================
# FACTORY FUNCTION
# =====================================================================

def create_document_agent(llm=None):
    """
    Create and return a DocumentAgent instance.
    """
    return DocumentAgent(llm=llm)
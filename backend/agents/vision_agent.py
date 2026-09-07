

from typing import Optional

from langsmith import traceable

from backend.tools.vision_inspector import analyze_structural_image


class VisionAgent:

    def __init__(self):
        self.name = "BuildWise Vision Agent"

    # -----------------------------------------------------------------
    # LangSmith Trace
    # -----------------------------------------------------------------

    @traceable(
        name="BuildWise Vision Agent",
        process_inputs=lambda inputs: {
            "file_name": inputs.get("file_name"),
            "query": inputs.get("user_input"),
            "language": inputs.get("language"),
        },
        process_outputs=lambda output: {
            "status": "completed"
        }
    )
    def process(
        self,
        file_bytes: Optional[bytes],
        file_name: Optional[str],
        user_input: str,
        language: str = "English"
    ) -> str:
        """
        Analyze a construction image.

        The actual vision analysis is handled by
        vision_inspector.py.

        LangSmith traces this Vision Agent execution
        without storing the uploaded image bytes.
        """

        is_bangla = language.lower() == "bangla"

        # -------------------------------------------------------------
        # Validate image
        # -------------------------------------------------------------

        if not file_bytes:

            if is_bangla:
                return (
                    "🖼️ **কোনো ছবি পাওয়া যায়নি।**\n\n"
                    "দয়া করে একটি construction image upload করুন।"
                )

            return (
                "🖼️ **No image uploaded.**\n\n"
                "Please upload a construction image "
                "before starting the inspection."
            )

        # -------------------------------------------------------------
        # Existing Vision Inspection Tool
        # -------------------------------------------------------------

        try:

            result = analyze_structural_image(
                image_bytes=file_bytes,
                image_name=file_name or "uploaded_image",
                query=user_input,
                is_bangla=is_bangla
            )

            return result["formatted_report"]

        except Exception as e:

            print(f"[VisionAgent] Error: {e}")

            if is_bangla:
                return (
                    "❌ **ছবিটি বিশ্লেষণ করতে সমস্যা হয়েছে।**\n\n"
                    "দয়া করে আবার চেষ্টা করুন।"
                )

            return (
                "❌ **Image inspection failed.**\n\n"
                "Please try again with a valid construction image."
            )


# =====================================================================
# FACTORY FUNCTION
# =====================================================================

def create_vision_agent():
    """
    Create and return a VisionAgent instance.
    """
    return VisionAgent()
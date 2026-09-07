

import base64
import io
from typing import Dict, Any, Optional

import pymupdf
from PIL import Image

from backend.config import settings


# ============================================================
# CONSTANTS
# ============================================================

ALLOWED_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}

MAX_FILE_SIZE = 20 * 1024 * 1024

MAX_PDF_PAGES = 3


# ============================================================
# IMAGE VALIDATION
# ============================================================

def validate_image(
    image_bytes: bytes,
) -> Image.Image:

    if not image_bytes:
        raise ValueError(
            "No image was uploaded."
        )

    if len(image_bytes) > MAX_FILE_SIZE:
        raise ValueError(
            "Image is larger than 20 MB."
        )

    try:
        image = Image.open(
            io.BytesIO(image_bytes)
        )

        image.load()

    except Exception as e:
        raise ValueError(
            f"Invalid image file: {e}"
        )

    if image.format not in ALLOWED_IMAGE_FORMATS:
        raise ValueError(
            "Unsupported image format. "
            "Please upload JPG, PNG, or WEBP."
        )

    return image


# ============================================================
# IMAGE → BASE64
# ============================================================

def encode_image(
    image_bytes: bytes,
    image_format: str,
) -> str:

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    if image_format.upper() == "JPEG":
        mime_type = "image/jpeg"
    else:
        mime_type = (
            f"image/{image_format.lower()}"
        )

    return (
        f"data:{mime_type};base64,{encoded}"
    )


# ============================================================
# PDF → PNG IMAGES
# ============================================================

def pdf_to_images(
    pdf_bytes: bytes,
) -> list:

    if not pdf_bytes:
        raise ValueError(
            "No PDF data was received."
        )

    if len(pdf_bytes) > MAX_FILE_SIZE:
        raise ValueError(
            "PDF is larger than 20 MB."
        )

    try:
        pdf_document = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

    except Exception as e:
        raise ValueError(
            f"Invalid PDF file: {e}"
        )

    if pdf_document.page_count == 0:

        pdf_document.close()

        raise ValueError(
            "The PDF does not contain any pages."
        )

    images = []

    pages_to_process = min(
        pdf_document.page_count,
        MAX_PDF_PAGES
    )

    try:

        for page_index in range(
            pages_to_process
        ):

            page = pdf_document.load_page(
                page_index
            )

            matrix = pymupdf.Matrix(
                1.8,
                1.8
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            png_bytes = pixmap.tobytes(
                "png"
            )

            images.append(
                (
                    page_index + 1,
                    png_bytes
                )
            )

    finally:

        pdf_document.close()

    return images


# ============================================================
# LANGUAGE
# ============================================================

def get_language_instruction(
    is_bangla: bool,
) -> str:

    if is_bangla:

        return """
Answer primarily in Bangla.

Keep important construction,
civil engineering, structural,
architectural and material terms
in English where appropriate.
"""

    return """
Answer in clear and simple English.
"""


# ============================================================
# PROMPT
# ============================================================

def build_vision_prompt(
    query: str,
    is_bangla: bool,
    source_type: str = "image",
    page_number: Optional[int] = None,
) -> str:

    language_instruction = (
        get_language_instruction(
            is_bangla
        )
    )

    user_question = query.strip()

    if not user_question:

        user_question = (
            "Inspect this construction image "
            "and identify visible "
            "construction-related conditions."
        )

    page_info = ""

    if (
        source_type == "pdf"
        and page_number is not None
    ):

        page_info = (
            f"\nThis image represents "
            f"PDF page {page_number}."
        )

    return f"""
You are BuildWise AI's Construction Vision Inspector.

You are analyzing an actual construction-related
visual input.

SOURCE TYPE:
{source_type}
{page_info}

USER QUESTION:
{user_question}

Analyze the provided visual input carefully.

IMPORTANT RULES:

1. Analyze ONLY what is actually visible.

2. Do NOT invent defects, objects, dimensions,
   labels, measurements or materials.

3. Do NOT assume that cracks, dampness,
   honeycombing, exposed reinforcement,
   corrosion or structural failure exist
   unless there is visible evidence.

4. If something is unclear, explicitly say:
   "Not clearly visible" or
   "Cannot be confirmed from the image."

5. Do NOT claim that a building is definitely
   safe or unsafe based only on an image.

6. Do NOT provide a definitive structural
   engineering diagnosis.

7. If something appears potentially serious,
   recommend inspection by a qualified
   structural engineer.

8. Separate clearly:
   - Visible observations
   - Possible concerns
   - Uncertain information

9. If this is a blueprint, floor plan,
   architectural drawing or construction
   document, identify rooms, labels,
   dimensions, structural members and
   symbols ONLY when readable.

10. Never invent measurements.

11. Never guess unreadable text.

12. Do not infer concrete grade,
    reinforcement diameter, structural
    capacity, foundation condition or
    material strength unless explicitly
    visible and readable.

13. If image quality is poor, mention it.

14. Keep the answer practical and concise.

15. DO NOT include your internal reasoning,
    thinking process, analysis draft or
    <think> tags in the answer.

{language_instruction}

Use exactly this structure:

### Visual Inspection

Directly answer the user's question.

### Visible Observations

List important things that are clearly visible.

### Possible Concerns

Mention possible concerns only when supported
by visible evidence.

### Recommended Action

Give general and safe next steps.

### Limitation

Explain that image-based inspection cannot
replace an on-site professional structural
assessment.
"""


# ============================================================
# GROQ VISION
# ============================================================

def analyze_with_groq_vision(
    image_bytes: bytes,
    image_format: str,
    query: str = "",
    is_bangla: bool = False,
    source_type: str = "image",
    page_number: Optional[int] = None,
) -> str:

    if not settings.GROQ_API_KEY:

        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    vision_model = getattr(
        settings,
        "GROQ_VISION_MODEL",
        "qwen/qwen3.6-27b"
    )

    from groq import Groq

    client = Groq(
        api_key=settings.GROQ_API_KEY
    )

    prompt = build_vision_prompt(
        query=query,
        is_bangla=is_bangla,
        source_type=source_type,
        page_number=page_number,
    )

    image_data = encode_image(
        image_bytes=image_bytes,
        image_format=image_format,
    )

    response = client.chat.completions.create(

        model=vision_model,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are BuildWise AI's "
                    "construction vision inspector. "
                    "Only report information supported "
                    "by visible evidence."
                ),
            },

            {
                "role": "user",
                "content": [

                    {
                        "type": "text",
                        "text": prompt,
                    },

                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        },
                    },

                ],
            },
        ],

        # Hide model reasoning from user
        reasoning_format="hidden",

        # Use non-thinking mode for efficient
        # general visual inspection
        reasoning_effort="none",

        temperature=0.2,

        # Reduced from 1500 to stay within
        # the current Groq output-token limit
        max_completion_tokens=700,
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:

        raise ValueError(
            "Groq Vision returned an empty response."
        )

    return content.strip()


# ============================================================
# NORMAL IMAGE ANALYSIS
# ============================================================

def analyze_normal_image(
    image_bytes: bytes,
    image_name: Optional[str],
    query: str,
    is_bangla: bool,
) -> Dict[str, Any]:

    image = validate_image(
        image_bytes
    )

    image_info = {
        "format": image.format,
        "size": (
            f"{image.width}x"
            f"{image.height}"
        ),
        "mode": image.mode,
        "source": "image",
    }

    report = analyze_with_groq_vision(
        image_bytes=image_bytes,
        image_format=image.format,
        query=query,
        is_bangla=is_bangla,
        source_type="image",
    )

    return {
        "image_name": image_name,
        "image_info": image_info,
        "severity": "AI visual assessment",
        "formatted_report": report,
        "analysis_status": "success",
    }


# ============================================================
# PDF ANALYSIS
# ============================================================

def analyze_pdf(
    pdf_bytes: bytes,
    pdf_name: Optional[str],
    query: str,
    is_bangla: bool,
) -> Dict[str, Any]:

    pdf_images = pdf_to_images(
        pdf_bytes
    )

    reports = []

    for page_number, page_image_bytes in pdf_images:

        try:

            page_report = analyze_with_groq_vision(
                image_bytes=page_image_bytes,
                image_format="PNG",
                query=query,
                is_bangla=is_bangla,
                source_type="pdf",
                page_number=page_number,
            )

            if is_bangla:

                heading = (
                    f"\n\n## 📄 PDF পৃষ্ঠা "
                    f"{page_number}\n\n"
                )

            else:

                heading = (
                    f"\n\n## 📄 PDF Page "
                    f"{page_number}\n\n"
                )

            reports.append(
                heading + page_report
            )

        except Exception as e:

            print(
                f"[Vision Inspector] "
                f"PDF page {page_number} error: {e}"
            )

            if is_bangla:

                reports.append(
                    f"\n\n## 📄 PDF পৃষ্ঠা "
                    f"{page_number}\n\n"
                    "⚠️ এই পৃষ্ঠাটি বিশ্লেষণ করা যায়নি।"
                )

            else:

                reports.append(
                    f"\n\n## 📄 PDF Page "
                    f"{page_number}\n\n"
                    "⚠️ This page could not be analyzed."
                )

    if not reports:

        raise ValueError(
            "No PDF pages could be analyzed."
        )

    pages_analyzed = len(
        pdf_images
    )

    if is_bangla:

        intro = (
            "📄 **PDF Visual Inspection Report**\n\n"
            f"Analyzed {pages_analyzed} page(s) "
            "from the uploaded PDF."
        )

        limitation = (
            "\n\n---\n\n"
            "⚠️ **সীমাবদ্ধতা:** "
            "এটি image-based preliminary analysis। "
            "এটি professional on-site structural "
            "inspection-এর বিকল্প নয়।"
        )

    else:

        intro = (
            "📄 **PDF Visual Inspection Report**\n\n"
            f"Analyzed {pages_analyzed} page(s) "
            "from the uploaded PDF."
        )

        limitation = (
            "\n\n---\n\n"
            "⚠️ **Limitation:** "
            "This is an image-based preliminary "
            "analysis and cannot replace a "
            "professional on-site structural "
            "inspection."
        )

    final_report = (
        intro
        + "".join(reports)
        + limitation
    )

    return {
        "image_name": pdf_name,
        "image_info": {
            "format": "PDF",
            "pages_analyzed": pages_analyzed,
            "source": "pdf",
        },
        "severity": "AI visual assessment",
        "formatted_report": final_report,
        "analysis_status": "success",
    }


# ============================================================
# MAIN FUNCTION
# ============================================================

def analyze_structural_image(
    image_bytes: Optional[bytes] = None,
    image_name: Optional[str] = None,
    query: str = "",
    is_bangla: bool = False,
) -> Dict[str, Any]:
    """
    Main Vision Inspector.

    Supports:
    JPG / JPEG / PNG / WEBP / PDF
    """

    # --------------------------------------------------------
    # No file
    # --------------------------------------------------------

    if not image_bytes:

        if is_bangla:

            message = (
                "⚠️ **কোনো ফাইল পাওয়া যায়নি।**\n\n"
                "দয়া করে একটি construction image, "
                "blueprint অথবা PDF upload করুন।"
            )

        else:

            message = (
                "⚠️ **No file was uploaded.**\n\n"
                "Please upload a construction image, "
                "blueprint, or PDF."
            )

        return {
            "image_name": image_name,
            "image_info": {},
            "severity": "Unknown",
            "formatted_report": message,
            "analysis_status": "no_file",
        }

    try:

        # ----------------------------------------------------
        # Detect PDF
        # ----------------------------------------------------

        is_pdf = False

        if image_name:

            if image_name.lower().endswith(
                ".pdf"
            ):
                is_pdf = True

        # PDF magic bytes
        if image_bytes[:4] == b"%PDF":

            is_pdf = True

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if is_pdf:

            return analyze_pdf(
                pdf_bytes=image_bytes,
                pdf_name=image_name,
                query=query,
                is_bangla=is_bangla,
            )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        return analyze_normal_image(
            image_bytes=image_bytes,
            image_name=image_name,
            query=query,
            is_bangla=is_bangla,
        )

    # --------------------------------------------------------
    # Validation error
    # --------------------------------------------------------

    except ValueError as e:

        print(
            f"[Vision Inspector] "
            f"Validation error: {e}"
        )

        if is_bangla:

            message = (
                "⚠️ **ফাইলটি বিশ্লেষণ করা যায়নি।**\n\n"
                f"{str(e)}"
            )

        else:

            message = (
                "⚠️ **The file could not be analyzed.**\n\n"
                f"{str(e)}"
            )

        return {
            "image_name": image_name,
            "image_info": {},
            "severity": "Unknown",
            "formatted_report": message,
            "analysis_status": "validation_error",
            "error": str(e),
        }

    # --------------------------------------------------------
    # General error
    # --------------------------------------------------------

    except Exception as e:

        print(
            f"[Vision Inspector] Error: {e}"
        )

        if is_bangla:

            message = (
                "⚠️ **Visual inspection সম্পন্ন করা যায়নি।**\n\n"
                "Groq Vision বা PDF processing-এ "
                "সমস্যা হয়েছে।\n\n"
                "দয়া করে আবার চেষ্টা করুন।"
            )

        else:

            message = (
                "⚠️ **Visual inspection could not "
                "be completed.**\n\n"
                "There was a problem with Groq Vision "
                "or PDF processing.\n\n"
                "Please try again."
            )

        return {
            "image_name": image_name,
            "image_info": {},
            "severity": "Unknown",
            "formatted_report": message,
            "analysis_status": "error",
            "error": str(e),
        }
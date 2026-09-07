import streamlit as st
import os
import mimetypes
from datetime import datetime
import uuid
import copy
import json
import re


# =====================================================================
# 1. PAGE CONFIGURATION
# =====================================================================

st.set_page_config(
    page_title="BuildWiseAI - Your Smart Construction Assistant",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================================
# 2. CUSTOM CSS
# =====================================================================

st.markdown("""
<style>

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: 'Plus Jakarta Sans', -apple-system,
        BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 2rem !important;
        max-width: 1040px !important;
    }

    header[data-testid="stHeader"] {
        height: 0px !important;
        min-height: 0px !important;
        padding: 0 !important;
    }


    /* ================================================================
       HIDE STREAMLIT HEADING ANCHOR / LOCALHOST LINKS
       ================================================================ */

    a[href^="#"] {
        display: none !important;
    }


    /* ================================================================
       SIDEBAR
       ================================================================ */

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
    }

    .tagline-badge {
        background: linear-gradient(
            135deg,
            #eef2ff 0%,
            #f5f3ff 100%
        );

        border: 1px solid #c7d2fe;
        border-radius: 8px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 700;
        color: #4f46e5;
        display: inline-block;
        margin-top: 2px;
        margin-bottom: 6px;
    }

    .dev-credit {
        font-size: 11px;
        font-weight: 500;
        color: #94a3b8;
        margin-top: 2px;
        margin-bottom: 12px;
    }

    .sidebar-newchat div.stButton > button {
        background: linear-gradient(
            135deg,
            #6366f1 0%,
            #4f46e5 100%
        ) !important;

        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 24px !important;
        padding: 10px !important;
        border: none !important;

        box-shadow:
            0 4px 14px rgba(79, 70, 229, 0.3) !important;
    }

    .sidebar-newchat div.stButton > button:hover {
        background: linear-gradient(
            135deg,
            #4f46e5 0%,
            #4338ca 100%
        ) !important;

        color: #ffffff !important;

        box-shadow:
            0 6px 18px rgba(79, 70, 229, 0.45) !important;
    }

    .chat-history-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 14px;
        margin-top: 6px;
        font-size: 13px;
        font-weight: 600;
        color: #334155;
    }

    .chat-history-title {
        font-size: 12px;
        font-weight: 700;
        color: #64748b;
        margin-bottom: 8px;
    }

    .history-delete div.stButton > button {
        width: 100% !important;
        min-height: 38px !important;
        padding: 6px 4px !important;
        border-radius: 10px !important;
        color: #ef4444 !important;
        border: 1px solid #fecaca !important;
        background: #fffafa !important;
        font-size: 15px !important;
    }

    .history-delete div.stButton > button:hover {
        background: #fee2e2 !important;
        border-color: #fca5a5 !important;
        color: #dc2626 !important;
    }

    .history-open div.stButton > button {
        width: 100% !important;
        text-align: left !important;
        border-radius: 10px !important;
        padding: 8px 10px !important;
        min-height: 38px !important;
        font-size: 12px !important;
    }

    .sidebar-footer {
        font-size: 10.5px;
        color: #94a3b8;
        text-align: center;
        margin-top: 18px;
    }


    /* ================================================================
       BUTTONS
       ================================================================ */

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {

        border-radius: 24px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;

        transition: all 0.25s ease-in-out !important;

        border: 1px solid #e2e8f0 !important;

        background: #ffffff !important;
        color: #334155 !important;

        width: 100% !important;
    }

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {

        background: #4f46e5 !important;
        color: #ffffff !important;
        border-color: #4f46e5 !important;

        box-shadow:
            0 4px 12px rgba(79, 70, 229, 0.25) !important;
    }

    div.stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {

        background: #4f46e5 !important;
        color: #ffffff !important;
        border-color: #4f46e5 !important;

        box-shadow:
            0 4px 12px rgba(79, 70, 229, 0.25) !important;
    }


    /* ================================================================
       FEATURE CARDS
       ================================================================ */

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    div.stButton > button {

        min-height: 90px !important;

        border-radius: 16px !important;

        font-size: 13.5px !important;
        font-weight: 700 !important;

        line-height: 1.35 !important;

        white-space: pre-line !important;

        padding: 12px 10px !important;

        border-width: 1.8px !important;

        background: #ffffff !important;

        transition: all 0.25s ease-in-out !important;

        box-shadow:
            0 4px 14px rgba(0, 0, 0, 0.03) !important;
    }


    /* Document */

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    > div:nth-child(1)
    div.stButton > button {

        border-color: #c7d2fe !important;
        color: #4f46e5 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    > div:nth-child(1)
    div.stButton > button:hover {

        background: #eef2ff !important;
        border-color: #6366f1 !important;
        color: #4338ca !important;

        transform: translateY(-2px) !important;

        box-shadow:
            0 6px 20px rgba(99, 102, 241, 0.22) !important;
    }


    /* Visual */

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    > div:nth-child(2)
    div.stButton > button {

        border-color: #bae6fd !important;
        color: #0284c7 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    > div:nth-child(2)
    div.stButton > button:hover {

        background: #f0f9ff !important;
        border-color: #0ea5e9 !important;
        color: #0369a1 !important;

        transform: translateY(-2px) !important;

        box-shadow:
            0 6px 20px rgba(14, 165, 233, 0.22) !important;
    }


    /* Cost */

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    > div:nth-child(3)
    div.stButton > button {

        border-color: #bbf7d0 !important;
        color: #16a34a !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    > div:nth-child(3)
    div.stButton > button:hover {

        background: #f0fdf4 !important;
        border-color: #22c55e !important;
        color: #15803d !important;

        transform: translateY(-2px) !important;

        box-shadow:
            0 6px 20px rgba(34, 197, 94, 0.22) !important;
    }


    /* Market */

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    > div:nth-child(4)
    div.stButton > button {

        border-color: #fed7aa !important;
        color: #ea580c !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div:nth-child(4))
    > div:nth-child(4)
    div.stButton > button:hover {

        background: #fff7ed !important;
        border-color: #f97316 !important;
        color: #c2410c !important;

        transform: translateY(-2px) !important;

        box-shadow:
            0 6px 20px rgba(249, 115, 22, 0.22) !important;
    }


    /* ================================================================
       HERO IMAGE
       ================================================================ */

    [data-testid="stImage"] img {

        max-height: 280px;

        width: 100%;

        object-fit: cover;

        object-position: center;

        border-radius: 16px;

        filter: brightness(0.92);
    }


    /* ================================================================
       WELCOME
       ================================================================ */

    .hero-welcome-title {

        font-size: 20px;

        font-weight: 800;

        color: #0f172a;

        margin-bottom: 2px;
    }

    .hero-welcome-subtitle {

        font-size: 13.5px;

        color: #64748b;

        font-weight: 500;
    }


    /* ================================================================
       CHAT
       ================================================================ */

    [data-testid="stChatMessage"] {

        padding: 14px 18px !important;

        border-radius: 16px !important;

        margin-bottom: 12px !important;

        font-size: 14.5px !important;

        line-height: 1.65 !important;
    }

    [data-testid="stChatMessage"]:has(
        [data-testid="stChatMessageAvatarUser"]
    ) {

        background: #eef2ff !important;

        border: 1.5px solid #c7d2fe !important;

        color: #1e1b4b !important;
    }

    [data-testid="stChatMessage"]:has(
        [data-testid="stChatMessageAvatarAssistant"]
    ) {

        background: #ffffff !important;

        border: 1.5px solid #e2e8f0 !important;

        box-shadow:
            0 4px 14px rgba(0,0,0,0.03) !important;

        color: #1e293b !important;
    }

</style>
""", unsafe_allow_html=True)


# =====================================================================
# 3. CONSTANTS
# =====================================================================

BACKEND_API_URL = "http://127.0.0.1:8000" 
 
FEATURE_NAMES = { 
    "general": "General Assistant", 
    "doc": "Document Analyzer", 
    "visual": "Visual Inspector", 
    "cost": "Cost Estimator", 
    "market": "Market Search" 
} 
 
FEATURE_ICONS = { 
    "general": "🤖", 
    "doc": "📄", 
    "visual": "🖼️", 
    "cost": "💰", 
    "market": "🔎" 
} 
 
FEATURE_KEYS = [ 
    "general", 
    "doc", 
    "visual", 
    "cost", 
    "market" 
] 
 
 
# ===================================================================== 
# 4. CHAT HISTORY PERSISTENCE 
# ===================================================================== 
 
CHAT_HISTORY_FILE = os.path.join( 
    os.path.dirname(__file__), 
    "chat_history.json" 
) 
 
 
def load_chat_history(): 
    """ 
    Load saved chat history from local JSON file. 
    """ 
 
    if not os.path.exists(CHAT_HISTORY_FILE): 
        return [] 
 
    try: 
 
        with open( 
            CHAT_HISTORY_FILE, 
            "r", 
            encoding="utf-8" 
        ) as f: 
 
            history = json.load(f) 
 
        if isinstance(history, list): 
            return history 
 
    except ( 
        json.JSONDecodeError, 
        OSError 
    ): 
        pass 
 
    return [] 
 
 
def save_chat_history(): 
    """ 
    Save current chat history to local JSON file. 
    """ 
 
    try: 
 
        with open( 
            CHAT_HISTORY_FILE, 
            "w", 
            encoding="utf-8" 
        ) as f: 
 
            json.dump( 
                st.session_state.chat_history, 
                f, 
                ensure_ascii=False, 
                indent=2 
            ) 
 
    except OSError: 
        pass 
 
 
# ===================================================================== 
# 5. SESSION STATE 
# ===================================================================== 
 
if "active_feature" not in st.session_state: 
    st.session_state.active_feature = None 
 
if "chat_history" not in st.session_state: 
    st.session_state.chat_history = load_chat_history() 
 
if "current_chat" not in st.session_state: 
    st.session_state.current_chat = { 
        "id": str(uuid.uuid4()), 
        "title": "New Chat", 
        "feature": "general", 
        "messages": { 
            feature: [] 
            for feature in FEATURE_KEYS 
        }, 
        "created_at": datetime.now().strftime( 
            "%d %b %Y, %I:%M %p" 
        ), 
        "updated_at": datetime.now().strftime( 
            "%d %b %Y, %I:%M %p" 
        ) 
    } 
 
if "uploader_version" not in st.session_state: 
    st.session_state.uploader_version = 0 
 
if "uploaded_doc_name" not in st.session_state: 
    st.session_state.uploaded_doc_name = None 
 
if "uploaded_doc_bytes" not in st.session_state: 
    st.session_state.uploaded_doc_bytes = None 
 
if "uploaded_image_name" not in st.session_state: 
    st.session_state.uploaded_image_name = None 
 
if "uploaded_image_bytes" not in st.session_state: 
    st.session_state.uploaded_image_bytes = None 
 
 
# ===================================================================== 
# 6. CHAT HELPER FUNCTIONS 
# ===================================================================== 
 
def get_current_feature(): 
    return ( 
        st.session_state.active_feature 
        if st.session_state.active_feature 
        else "general" 
    ) 
 
 
def get_current_messages(feature=None): 
 
    if feature is None: 
        feature = get_current_feature() 
 
    return st.session_state.current_chat["messages"].setdefault( 
        feature, 
        [] 
    ) 
 
 
def add_message(role, content, feature=None): 
 
    if feature is None: 
        feature = get_current_feature() 
 
    st.session_state.current_chat["messages"].setdefault( 
        feature, 
        [] 
    ).append({ 
        "role": role, 
        "content": content, 
        "feature": feature 
    }) 
 
    st.session_state.current_chat["feature"] = feature 
 
    st.session_state.current_chat["updated_at"] = ( 
        datetime.now().strftime( 
            "%d %b %Y, %I:%M %p" 
        ) 
    ) 
 
 
def has_messages(chat): 
 
    return any( 
        len( 
            chat.get( 
                "messages", 
                {} 
            ).get( 
                feature, 
                [] 
            ) 
        ) > 0 
        for feature in FEATURE_KEYS 
    ) 
 
 
def create_chat_title(chat): 
    """ 
    Create history title from the first user message 
    across all features. 
    """ 
 
    for feature in FEATURE_KEYS: 
 
        messages = chat.get( 
            "messages", 
            {} 
        ).get( 
            feature, 
            [] 
        ) 
 
        for message in messages: 
 
            if message.get("role") == "user": 
 
                text = message.get( 
                    "content", 
                    "" 
                ).replace( 
                    "\n", 
                    " " 
                ).strip() 
 
                if text: 
 
                    if len(text) > 34: 
                        text = ( 
                            text[:34].rstrip() 
                            + "..." 
                        ) 
 
                    return ( 
                        f"{FEATURE_ICONS.get(feature, '💬')} " 
                        f"{text}" 
                    ) 
 
    return "💬 New Chat" 
 
 
def save_current_chat(): 
    """ 
    Save/update the current conversation in history. 
 
    One chat session = one history item. 
    All questions from that session stay together. 
    """ 
 
    current_chat = st.session_state.current_chat 
 
    if not has_messages(current_chat): 
        return 
 
    chat_copy = copy.deepcopy( 
        current_chat 
    ) 
 
    chat_copy["title"] = create_chat_title( 
        chat_copy 
    ) 
 
    chat_copy["updated_at"] = ( 
        datetime.now().strftime( 
            "%d %b %Y, %I:%M %p" 
        ) 
    ) 
 
    chat_id = chat_copy["id"] 
 
    # Remove old copy if already present 
    st.session_state.chat_history = [ 
        chat 
        for chat in st.session_state.chat_history 
        if chat["id"] != chat_id 
    ] 
 
    # Put latest version at top 
    st.session_state.chat_history.insert( 
        0, 
        chat_copy 
    ) 
 
    # Persist history to disk 
    save_chat_history() 
 
 
def clear_feature_files(): 
    """ 
    Completely clear uploaded document/image. 
    """ 
 
    st.session_state.uploaded_doc_name = None 
    st.session_state.uploaded_doc_bytes = None 
 
    st.session_state.uploaded_image_name = None 
    st.session_state.uploaded_image_bytes = None 
 
 
def reset_uploaders(): 
    """ 
    Change uploader key so Streamlit creates a fresh uploader. 
    """ 
 
    st.session_state.uploader_version += 1 
 
    clear_feature_files() 
 
 
def start_new_chat(): 
    """ 
    Create a completely fresh chat. 
 
    Previous chat is saved first. 
    """ 
 
    save_current_chat() 
 
    st.session_state.current_chat = { 
        "id": str(uuid.uuid4()), 
        "title": "New Chat", 
        "feature": "general", 
        "messages": { 
            feature: [] 
            for feature in FEATURE_KEYS 
        }, 
        "created_at": datetime.now().strftime( 
            "%d %b %Y, %I:%M %p" 
        ), 
        "updated_at": datetime.now().strftime( 
            "%d %b %Y, %I:%M %p" 
        ) 
    } 
 
    st.session_state.active_feature = None 
 
    reset_uploaders() 
 
 
def load_chat(chat_id): 
    """ 
    Load a previous chat. 
    """ 
 
    # Save current unsaved conversation first 
    save_current_chat() 
 
    selected_chat = None 
 
    for chat in st.session_state.chat_history: 
 
        if chat["id"] == chat_id: 
            selected_chat = chat 
            break 
 
    if selected_chat is None: 
        return 
 
    st.session_state.current_chat = copy.deepcopy( 
        selected_chat 
    ) 
 
    st.session_state.active_feature = ( 
        selected_chat.get( 
            "feature", 
            "general" 
        ) 
    ) 
 
    reset_uploaders() 
 
 
def delete_chat(chat_id): 
    """ 
    Delete an entire chat session from history. 
    """ 
 
    st.session_state.chat_history = [ 
        chat 
        for chat in st.session_state.chat_history 
        if chat["id"] != chat_id 
    ] 
 
    # Persist deletion 
    save_chat_history() 
 
    # If deleting the currently opened chat, 
    # create a blank chat. 
    if ( 
        st.session_state.current_chat["id"] 
        == chat_id 
    ): 
 
        st.session_state.current_chat = { 
            "id": str(uuid.uuid4()), 
            "title": "New Chat", 
            "feature": "general", 
            "messages": { 
                feature: [] 
                for feature in FEATURE_KEYS 
            }, 
            "created_at": datetime.now().strftime( 
                "%d %b %Y, %I:%M %p" 
            ), 
            "updated_at": datetime.now().strftime( 
                "%d %b %Y, %I:%M %p" 
            ) 
        } 
 
        st.session_state.active_feature = None 
 
        reset_uploaders() 
 
 
# ===================================================================== 
# 7. BACKEND FUNCTIONS 
# ===================================================================== 
 
def send_to_backend( 
    feature: str, 
    user_input: str, 
    file_name: str = None, 
    file_bytes: bytes = None, 
    extra_data: dict = None 
) -> str: 
 
    import requests 
 
    mime_type = "application/octet-stream" 
 
    if file_name: 
 
        detected_type, _ = mimetypes.guess_type( 
            file_name 
        ) 
 
        if detected_type: 
            mime_type = detected_type 
 
        lower_name = file_name.lower() 
 
        if lower_name.endswith(".pdf"): 
            mime_type = "application/pdf" 
 
        elif lower_name.endswith(".docx"): 
            mime_type = ( 
                "application/vnd.openxmlformats-officedocument." 
                "wordprocessingml.document" 
            ) 
 
        elif lower_name.endswith(".txt"): 
            mime_type = "text/plain" 
 
        elif lower_name.endswith(".png"): 
            mime_type = "image/png" 
 
        elif ( 
            lower_name.endswith(".jpg") 
            or lower_name.endswith(".jpeg") 
        ): 
            mime_type = "image/jpeg" 
 
 
    # ============================================================= 
    # DOCUMENT ANALYZER 
    # ============================================================= 
 
    if feature == "doc": 
 
        if file_bytes: 
 
            try: 
 
                files = { 
                    "file": ( 
                        file_name or "document.pdf", 
                        file_bytes, 
                        mime_type 
                    ) 
                } 
 
                data = { 
                    "query": user_input 
                } 
 
                with st.spinner( 
                    "📄 Analyzing document with OCR + RAG..." 
                ): 
 
                    response = requests.post( 
                        f"{BACKEND_API_URL}/api/analyze-doc", 
                        files=files, 
                        data=data, 
                        timeout=180 
                    ) 
 
                if response.status_code == 200: 
 
                    result = response.json() 
 
                    if result.get("success") is False: 
 
                        return ( 
                            "❌ **Document Analyzer Error**\n\n" 
                            f"{result.get('error', 'Unknown backend error.')}" 
                        ) 
 
                    answer = result.get( 
                        "response" 
                    ) 
 
                    if answer: 
                        return answer 
 
                    return ( 
                        "❌ **Document Analyzer returned " 
                        "an empty response.**" 
                    ) 
 
                return ( 
                    "❌ **Document Analyzer backend error**\n\n" 
                    f"HTTP Status: `{response.status_code}`\n\n" 
                    f"{response.text[:2000]}" 
                ) 
 
            except requests.exceptions.Timeout: 
 
                return ( 
                    "⏱️ **Document analysis timed out.**\n\n" 
                    "Please try again." 
                ) 
 
            except requests.exceptions.ConnectionError: 
 
                return ( 
                    "🔌 **Cannot connect to BuildWiseAI backend.**\n\n" 
                    "Please make sure FastAPI is running:\n\n" 
                    "```bash\n" 
                    "python -m uvicorn backend.main:app --reload\n" 
                    "```" 
                ) 
 
            except Exception as e: 
 
                return ( 
                    "❌ **Document Analyzer error**\n\n" 
                    f"`{type(e).__name__}: {str(e)}`" 
                ) 
 
        else: 
 
            # No document = general construction AI 
            return send_general_chat( 
                user_input=user_input 
            ) 
 
 
    # ============================================================= 
    # VISUAL INSPECTOR 
    # ============================================================= 
 
    elif feature == "visual": 
 
        if not file_bytes: 
 
            return ( 
                "🖼️ **Please upload an image first.**\n\n" 
                "Upload your building image above, " 
                "then ask your question." 
            ) 
 
        try: 
 
            files = { 
                "file": ( 
                    file_name or "image.jpg", 
                    file_bytes, 
                    mime_type 
                ) 
            } 
 
            data = { 
                "query": user_input 
            } 
 
            with st.spinner( 
                "🖼️ Analyzing image with AI Vision..." 
            ): 
 
                response = requests.post( 
                    f"{BACKEND_API_URL}/api/inspect-image", 
                    files=files, 
                    data=data, 
                    timeout=120 
                ) 
 
            if response.status_code == 200: 
 
                result = response.json() 
 
                if result.get("success") is False: 
 
                    return ( 
                        "❌ **Visual Inspector Error**\n\n" 
                        f"{result.get('error', 'Unknown backend error.')}" 
                    ) 
 
                answer = result.get( 
                    "response", 
                    "" 
                ) 
 
                if answer: 
                    return answer 
 
                return ( 
                    "❌ **Visual Inspector returned " 
                    "an empty response.**" 
                ) 
 
            return ( 
                "❌ **Visual Inspector backend error**\n\n" 
                f"HTTP Status: `{response.status_code}`\n\n" 
                f"{response.text[:1500]}" 
            ) 
 
        except requests.exceptions.Timeout: 
 
            return ( 
                "⏱️ **Vision analysis timed out.**\n\n" 
                "Please try again." 
            ) 
 
        except requests.exceptions.ConnectionError: 
 
            return ( 
                "🔌 **Cannot connect to BuildWiseAI backend.**\n\n" 
                "Please start FastAPI first." 
            ) 
 
        except Exception as e: 
 
            return ( 
                "❌ **Visual Inspector error**\n\n" 
                f"`{type(e).__name__}: {str(e)}`" 
            ) 
 
 
    # ============================================================= 
    # COST ESTIMATOR 
    # ============================================================= 
 
    elif feature == "cost" and extra_data: 
 
        try: 
 
            payload = { 
                "building_type": extra_data.get( 
                    "building_type", 
                    "Residential" 
                ), 
 
                "area_sqft": extra_data.get( 
                    "area_sqft", 
                    1500 
                ), 
 
                "floors": extra_data.get( 
                    "floors", 
                    1 
                ), 
 
                "quality": extra_data.get( 
                    "quality", 
                    "Standard" 
                ), 
 
                "notes": extra_data.get( 
                    "notes", 
                    "" 
                ) 
            } 
 
            with st.spinner( 
                "💰 Calculating construction cost..." 
            ): 
 
                response = requests.post( 
                    f"{BACKEND_API_URL}/api/estimate-cost", 
                    json=payload, 
                    timeout=30 
                ) 
 
            if response.status_code == 200: 
 
                result = response.json() 
 
                if result.get("success") is False: 
 
                    return ( 
                        "❌ **Cost Estimator Error**\n\n" 
                        f"{result.get('error', 'Unknown backend error.')}" 
                    ) 
 
                answer = result.get( 
                    "response", 
                    "" 
                ) 
 
                if answer: 
                    return answer 
 
                return ( 
                    "❌ Cost estimator returned " 
                    "an empty response." 
                ) 
 
            return ( 
                "❌ **Cost Estimator Error**\n\n" 
                f"HTTP Status: `{response.status_code}`\n\n" 
                f"{response.text[:1000]}" 
            ) 
 
        except Exception as e: 
 
            return ( 
                "❌ **Cost Estimator error**\n\n" 
                f"`{type(e).__name__}: {str(e)}`" 
            ) 
 
 
    # ============================================================= 
    # MARKET SEARCH 
    # ============================================================= 
 
    elif feature == "market": 
 
        try: 
 
            payload = { 
                "query": user_input 
            } 
 
            with st.spinner( 
                "🔎 Searching construction market..." 
            ): 
 
                response = requests.post( 
                    f"{BACKEND_API_URL}/api/market-search", 
                    json=payload, 
                    timeout=60 
                ) 
 
            if response.status_code == 200: 
 
                result = response.json() 
 
                if result.get("success") is False: 
 
                    return ( 
                        "❌ **Market Search Error**\n\n" 
                        f"{result.get('error', 'Unknown backend error.')}" 
                    ) 
 
                answer = result.get( 
                    "response", 
                    "" 
                ) 
 
                if answer: 
                    return answer 
 
                return ( 
                    "❌ Market Search returned " 
                    "an empty response." 
                ) 
 
            return ( 
                "❌ **Market Search Error**\n\n" 
                f"HTTP Status: `{response.status_code}`\n\n" 
                f"{response.text[:1000]}" 
            ) 
 
        except requests.exceptions.ConnectionError: 
 
            return ( 
                "🔌 **Cannot connect to BuildWiseAI backend.**\n\n" 
                "Please start FastAPI first." 
            ) 
 
        except Exception as e: 
 
            return ( 
                "❌ **Market Search error**\n\n" 
                f"`{type(e).__name__}: {str(e)}`" 
            ) 
 
 
    # ============================================================= 
    # GENERAL 
    # ============================================================= 
 
    else: 
 
        return send_general_chat( 
            user_input=user_input 
        ) 
 
 
# ===================================================================== 
# 8. GENERAL CHAT 
# ===================================================================== 
 
def send_general_chat( 
    user_input: str 
) -> str: 
 
    import requests 
 
    try: 
 
        payload = { 
            "message": user_input, 
            "feature": "general" 
        } 
 
        with st.spinner( 
            "🤖 BuildWiseAI is thinking..." 
        ): 
 
            response = requests.post( 
                f"{BACKEND_API_URL}/api/chat", 
                json=payload, 
                timeout=60 
            ) 
 
        if response.status_code == 200: 
 
            result = response.json() 
 
            if result.get("success") is False: 
 
                return ( 
                    "❌ **Assistant Error**\n\n" 
                    f"{result.get('error', 'Unknown backend error.')}" 
                ) 
 
            answer = result.get( 
                "response", 
                "" 
            ) 
 
            if answer: 
                return answer 
 
            return ( 
                "❌ Assistant returned " 
                "an empty response." 
            ) 
 
        return ( 
            "❌ **Assistant backend error**\n\n" 
            f"HTTP Status: `{response.status_code}`\n\n" 
            f"{response.text[:1000]}" 
        ) 
 
    except requests.exceptions.ConnectionError: 
 
        return ( 
            "🔌 **Cannot connect to BuildWiseAI backend.**\n\n" 
            "Please make sure FastAPI is running:\n\n" 
            "```bash\n" 
            "python -m uvicorn backend.main:app --reload\n" 
            "```" 
        ) 
 
    except requests.exceptions.Timeout: 
 
        return ( 
            "⏱️ **Assistant request timed out.**\n\n" 
            "Please try again." 
        ) 
 
    except Exception as e: 
 
        return ( 
            "❌ **Assistant error**\n\n" 
            f"`{type(e).__name__}: {str(e)}`" 
        ) 
 
 
# ===================================================================== 
# 9. SIDEBAR 
# ===================================================================== 
 
with st.sidebar: 
 
    st.markdown("### 🏗️ **BuildWiseAI**") 
 
    st.markdown( 
        '<div class="tagline-badge">' 
        '✨ Your Smart Construction Assistant' 
        '</div>', 
        unsafe_allow_html=True 
    ) 
 
    st.markdown( 
        '<div class="dev-credit">' 
        'Developed by Ismat Maksura' 
        '</div>', 
        unsafe_allow_html=True 
    ) 
 
 
    # ============================================================= 
    # NEW CHAT 
    # ============================================================= 
 
    st.markdown( 
        '<div class="sidebar-newchat">', 
        unsafe_allow_html=True 
    ) 
 
    if st.button( 
        "+ New Chat", 
        key="btn_new_chat", 
        width="stretch" 
    ): 
 
        start_new_chat() 
 
        st.rerun() 
 
    st.markdown( 
        '</div>', 
        unsafe_allow_html=True 
    ) 
 
 
    st.markdown( 
        "<br>", 
        unsafe_allow_html=True 
    ) 
 
 
    # ============================================================= 
    # CHAT HISTORY 
    # ============================================================= 
 
    st.markdown("**💬 Chat History**") 
 
    if not st.session_state.chat_history: 
 
        st.markdown( 
            """ 
            <div class="chat-history-card"> 
                <span style="color:#94a3b8;"> 
                    No previous chats yet 
                </span> 
            </div> 
            """, 
            unsafe_allow_html=True 
        ) 
 
    else: 
 
        # Show latest 8 conversations 
        for chat in st.session_state.chat_history[:8]: 
 
            icon = FEATURE_ICONS.get( 
                chat.get( 
                    "feature", 
                    "general" 
                ), 
                "💬" 
            ) 
 
            title = chat.get( 
                "title", 
                "Previous Chat" 
            ) 
 
            updated = chat.get( 
                "updated_at", 
                "" 
            ) 
 
            # Two columns: 
            # LEFT = open chat 
            # RIGHT = delete 
            history_col, delete_col = st.columns( 
                [5.5, 1], 
                gap="small" 
            ) 
 
            with history_col: 
 
                st.markdown( 
                    '<div class="history-open">', 
                    unsafe_allow_html=True 
                ) 
 
                if st.button( 
                    f"{icon} {title}", 
                    key=f"history_open_{chat['id']}", 
                    width="stretch" 
                ): 
 
                    load_chat( 
                        chat["id"] 
                    ) 
 
                    st.rerun() 
 
                st.markdown( 
                    '</div>', 
                    unsafe_allow_html=True 
                ) 
 
                if updated: 
 
                    st.caption( 
                        updated 
                    ) 
 
            with delete_col: 
 
                st.markdown( 
                    '<div class="history-delete">', 
                    unsafe_allow_html=True 
                ) 
 
                if st.button( 
                    "🗑️", 
                    key=f"history_delete_{chat['id']}", 
                    help="Delete this chat" 
                ): 
 
                    delete_chat( 
                        chat["id"] 
                    ) 
 
                    st.rerun() 
 
                st.markdown( 
                    '</div>', 
                    unsafe_allow_html=True 
                ) 
 
 
    st.markdown( 
        "<br><br>", 
        unsafe_allow_html=True 
    ) 
 
    st.divider() 
 
    st.markdown( 
        '<div class="sidebar-footer">' 
        'BuildWiseAI v1.0 · 2026' 
        '</div>', 
        unsafe_allow_html=True 
    ) 
 
 
# ===================================================================== 
# 10. FEATURE CARDS 
# ===================================================================== 
 
card_cols = st.columns(4) 
 
CARDS = [ 
 
    ( 
        "doc", 
        "📄", 
        "Document Analyzer", 
        "purple" 
    ), 
 
    ( 
        "visual", 
        "🖼️", 
        "Visual Inspector", 
        "blue" 
    ), 
 
    ( 
        "cost", 
        "💰", 
        "Cost Estimator", 
        "green" 
    ), 
 
    ( 
        "market", 
        "🔎", 
        "Market Search", 
        "orange" 
    ) 
] 
 
 
for col, ( 
    feat_key, 
    icon, 
    title, 
    color 
) in zip( 
    card_cols, 
    CARDS 
): 
 
    with col: 
 
        is_active = ( 
            st.session_state.active_feature 
            == feat_key 
        ) 
 
        card_label = ( 
            f"{icon}\n\n{title}" 
            + ( 
                "  ✓" 
                if is_active 
                else "" 
            ) 
        ) 
 
        if st.button( 
            card_label, 
            key=f"card_{feat_key}", 
            width="stretch" 
        ): 
 
            if is_active: 
 
                # Close current feature 
                st.session_state.active_feature = None 
 
                reset_uploaders() 
 
            else: 
 
                # Switch feature 
                st.session_state.active_feature = feat_key 
 
                # IMPORTANT: 
                # Uploaded files from another feature 
                # are completely cleared. 
                reset_uploaders() 
 
            st.session_state.current_chat["feature"] = ( 
                get_current_feature() 
            ) 
 
            st.rerun() 
 
 
st.markdown( 
    "<div style='margin-bottom:8px;'></div>", 
    unsafe_allow_html=True 
) 
 
 
# ===================================================================== 
# 11. HERO IMAGE 
# ===================================================================== 
 
hero_img_path = os.path.join( 
    "frontend", 
    "assets", 
    "building.jpg" 
) 
 
if not os.path.exists(hero_img_path): 
 
    hero_img_path = os.path.join( 
        os.path.dirname(__file__), 
        "assets", 
        "building.jpg" 
    ) 
 
 
if os.path.exists(hero_img_path): 
 
    st.image( 
        hero_img_path, 
        width="stretch" 
    ) 
 
else: 
 
    st.info( 
        "💡 Place 'building.jpg' inside " 
        "'frontend/assets/' to see the building image." 
    ) 
 
 
# ===================================================================== 
# 12. WELCOME MESSAGE 
# ===================================================================== 
 
welcome_title = ( 
    "Welcome to BuildWiseAI! 👋" 
) 
 
welcome_subtitle = ( 
    "Here I am to clear all your building " 
    "confusions and queries" 
) 
 
 
st.markdown( 
    f"### {welcome_title}" 
) 
 
st.markdown( 
    f""" 
    <div style='text-align:center; 
    color:#64748b; 
    font-size:13.5px; 
    font-weight:500; 
    margin-top:-10px; 
    margin-bottom:12px;'> 
    {welcome_subtitle} 
    </div> 
    """, 
    unsafe_allow_html=True 
) 
 
 
# ===================================================================== 
# 13. FEATURE INPUT AREA 
# ===================================================================== 
 
active = st.session_state.active_feature 
 
 
# ===================================================================== 
# DOCUMENT ANALYZER 
# ===================================================================== 
 
if active == "doc": 
 
    st.markdown( 
        "#### 📄 Document Analyzer" 
    ) 
 
    uploaded_file = st.file_uploader( 
        "Upload your document (PDF, DOCX, TXT)", 
        type=[ 
            "pdf", 
            "docx", 
            "txt" 
        ], 
        key=f"doc_upload_{st.session_state.uploader_version}" 
    ) 
 
    if uploaded_file is not None: 
 
        st.session_state.uploaded_doc_name = ( 
            uploaded_file.name 
        ) 
 
        st.session_state.uploaded_doc_bytes = ( 
            uploaded_file.getvalue() 
        ) 
 
        st.success( 
            f"✅ Uploaded: **{uploaded_file.name}** " 
            f"({round(uploaded_file.size / 1024, 1)} KB)" 
        ) 
 
 
# ===================================================================== 
# VISUAL INSPECTOR 
# ===================================================================== 
 
elif active == "visual": 
 
    st.markdown( 
        "#### 🖼️ Visual Inspector" 
    ) 
 
    uploaded_image = st.file_uploader( 
        "Upload an image (JPG, PNG, JPEG)", 
        type=[ 
            "jpg", 
            "jpeg", 
            "png" 
        ], 
        key=f"visual_upload_{st.session_state.uploader_version}" 
    ) 
 
    if uploaded_image is not None: 
 
        st.session_state.uploaded_image_name = ( 
            uploaded_image.name 
        ) 
 
        st.session_state.uploaded_image_bytes = ( 
            uploaded_image.getvalue() 
        ) 
 
        st.image( 
            uploaded_image, 
            caption=f"Uploaded: {uploaded_image.name}", 
            width=380 
        ) 
 
 
# ===================================================================== 
# COST ESTIMATOR 
# ===================================================================== 
 
elif active == "cost": 
 
    st.markdown( 
        "#### 💰 Cost Estimator" 
    ) 
 
    with st.form( 
        key="cost_form", 
        clear_on_submit=False 
    ): 
 
        c1, c2 = st.columns(2) 
 
        with c1: 
 
            building_type = st.selectbox( 
                "Building Type", 
                [ 
                    "Residential", 
                    "Commercial", 
                    "Industrial", 
                    "Duplex", 
                    "Semi-Pucca" 
                ], 
                key="cost_type" 
            ) 
 
        with c2: 
 
            area_sqft = st.number_input( 
                "Area (sq ft)", 
                min_value=100, 
                max_value=50000, 
                value=1500, 
                step=100, 
                key="cost_area" 
            ) 
 
        c3, c4 = st.columns(2) 
 
        with c3: 
 
            floors = st.selectbox( 
                "Number of Floors", 
                [ 
                    1, 
                    2, 
                    3, 
                    4, 
                    5, 
                    6, 
                    7, 
                    8, 
                    10 
                ], 
                key="cost_floors" 
            ) 
 
        with c4: 
 
            quality = st.selectbox( 
                "Finish Quality", 
                [ 
                    "Standard", 
                    "Medium", 
                    "Premium", 
                    "Luxury" 
                ], 
                key="cost_quality" 
            ) 
 
        cost_notes = st.text_input( 
            "Additional details (optional):", 
            placeholder=( 
                "e.g. Include basement parking, " 
                "rooftop solar, premium sanitary fixtures" 
            ), 
            key="cost_notes" 
        ) 
 
        submit_cost = st.form_submit_button( 
            "💰 Estimate Construction Cost", 
            width="stretch" 
        ) 
 
        if submit_cost: 
 
            user_input = ( 
                f"{building_type}, " 
                f"{area_sqft} sq ft, " 
                f"{floors} floors, " 
                f"{quality} finish quality" 
            ) 
 
            if cost_notes: 
 
                user_input += ( 
                    f", {cost_notes}" 
                ) 
 
            add_message( 
                "user", 
                f"[💰 Cost Estimator] {user_input}", 
                "cost" 
            ) 
 
            extra_data = { 
 
                "building_type": building_type, 
 
                "area_sqft": area_sqft, 
 
                "floors": floors, 
 
                "quality": quality, 
 
                "notes": cost_notes or "" 
            } 
 
            response = send_to_backend( 
                feature="cost", 
                user_input=user_input, 
                extra_data=extra_data 
            ) 
 
            add_message( 
                "assistant", 
                response, 
                "cost" 
            ) 
 
            save_current_chat() 
 
            st.rerun() 
 
 
# ===================================================================== 
# MARKET SEARCH 
# ===================================================================== 
 
elif active == "market": 
 
    st.markdown( 
        "#### 🔎 Market Search" 
    ) 
 
 
# ===================================================================== 
# 14. CONVERSATION FEED 
# ===================================================================== 
 
current_feature = get_current_feature() 
 
current_messages = get_current_messages( 
    current_feature 
) 
 
if current_messages: 
 
    st.markdown("---") 
 
    for msg in current_messages: 
 
        role = msg.get( 
            "role", 
            "user" 
        ) 
 
        avatar = ( 
            "👤" 
            if role == "user" 
            else "🏗️" 
        ) 
 
        with st.chat_message( 
            role, 
            avatar=avatar 
        ): 
 
            content = msg.get( 
                "content", 
                "" 
            )

            # Remove HTML line-break tags from AI responses
            content = re.sub(
                r"<br\s*/?>",
                "\n",
                content,
                flags=re.IGNORECASE
            )

            st.markdown(content)
 
 
# ===================================================================== 
# 15. CHAT INPUT 
# ===================================================================== 
 
chat_placeholder = ( 
    "💬 Type your message here..." 
) 
 
 
prompt = st.chat_input( 
    chat_placeholder 
) 
 
 
if prompt: 
 
    feature = get_current_feature() 
 
    # ============================================================= 
    # FILE VARIABLES 
    # ============================================================= 
 
    file_name = None 
    file_bytes = None 
 
 
    # ============================================================= 
    # DOCUMENT 
    # ============================================================= 
 
    if feature == "doc": 
 
        file_name = st.session_state.get( 
            "uploaded_doc_name" 
        ) 
 
        file_bytes = st.session_state.get( 
            "uploaded_doc_bytes" 
        ) 
 
 
    # ============================================================= 
    # VISUAL 
    # ============================================================= 
 
    elif feature == "visual": 
 
        file_name = st.session_state.get( 
            "uploaded_image_name" 
        ) 
 
        file_bytes = st.session_state.get( 
            "uploaded_image_bytes" 
        ) 
 
 
    # ============================================================= 
    # SAVE USER MESSAGE 
    # ============================================================= 
 
    add_message( 
        "user", 
        prompt, 
        feature 
    ) 
 
 
    # ============================================================= 
    # DOCUMENT 
    # ============================================================= 
 
    if feature == "doc": 
 
        response = send_to_backend( 
 
            feature="doc", 
 
            user_input=prompt, 
 
            file_name=file_name, 
 
            file_bytes=file_bytes 
        ) 
 
 
    # ============================================================= 
    # VISUAL 
    # ============================================================= 
 
    elif feature == "visual": 
 
        if not file_bytes: 
 
            response = ( 
                "🖼️ **Please upload an image first.**\n\n" 
                "Upload your building image above, " 
                "then ask your question." 
            ) 
 
        else: 
 
            response = send_to_backend( 
 
                feature="visual", 
 
                user_input=prompt, 
 
                file_name=file_name, 
 
                file_bytes=file_bytes 
            ) 
 
 
    # ============================================================= 
    # COST 
    # ============================================================= 
 
    elif feature == "cost": 
 
        response = ( 
            "💰 Please use the Cost Estimator form above " 
            "to calculate your construction cost." 
        ) 
 
 
    # ============================================================= 
    # MARKET 
    # ============================================================= 
 
    elif feature == "market": 
 
        response = send_to_backend( 
 
            feature="market", 
 
            user_input=prompt 
        ) 
 
 
    # ============================================================= 
    # GENERAL 
    # ============================================================= 
 
    else: 
 
        response = send_to_backend( 
 
            feature="general", 
 
            user_input=prompt 
        ) 
 
 
    # ============================================================= 
    # SAVE ASSISTANT MESSAGE 
    # ============================================================= 
 
    add_message( 
        "assistant", 
        response, 
        feature 
    ) 
 
 
    # ============================================================= 
    # SAVE / UPDATE CHAT HISTORY 
    # ============================================================= 
 
    save_current_chat() 
 
 
    st.rerun()

from typing import Dict, Any, Optional

from backend.config import settings
from backend.prompts.construction_prompts import SYSTEM_PROMPT_AGENT

# Router
from backend.agents.router_agent import router_agent

# Specialized Agents
from backend.agents.doc_agent import create_document_agent
from backend.agents.cost_agent import create_cost_agent
from backend.agents.search_agent import create_search_agent
from backend.agents.vision_agent import create_vision_agent


class ConstructionAgent:

    def __init__(self):
        """
        Initialize the BuildWise supervisor and all specialized agents.
        """

        self.name = "BuildWise Construction Supervisor"

        # Shared LLM
        self.llm = None
        self._init_llm()

        # -------------------------------------------------------------
        # Initialize specialized agents
        # -------------------------------------------------------------

        self.document_agent = create_document_agent(
            llm=self.llm
        )

        self.cost_agent = create_cost_agent()

        self.search_agent = create_search_agent()

        self.vision_agent = create_vision_agent()

    # =================================================================
    # GROQ LLM INITIALIZATION
    # =================================================================

    def _init_llm(self):
        """
        Initialize Groq LLM if API key is available.
        """

        if (
            settings.GROQ_API_KEY
            and settings.GROQ_API_KEY != "your_groq_api_key_here"
        ):

            try:

                from langchain_groq import ChatGroq

                self.llm = ChatGroq(
                    model=settings.GROQ_MODEL,
                    groq_api_key=settings.GROQ_API_KEY,
                    temperature=0.3
                )

                print(
                    f"[BuildWiseSupervisor] "
                    f"Groq LLM initialized: {settings.GROQ_MODEL}"
                )

            except Exception as e:

                print(
                    f"[BuildWiseSupervisor] "
                    f"Groq LLM initialization error: {e}"
                )

                self.llm = None

    # =================================================================
    # GENERAL CHAT
    # =================================================================

    def _general_chat(
        self,
        user_input: str,
        language: str
    ) -> str:
        """
        Handle general construction-related questions directly
        through the shared Groq LLM.
        """

        is_bangla = language.lower() == "bangla"

        # -------------------------------------------------------------
        # LLM available
        # -------------------------------------------------------------

        if self.llm:

            try:

                from langchain_core.messages import (
                    SystemMessage,
                    HumanMessage
                )

                sys_msg = SystemMessage(
                    content=SYSTEM_PROMPT_AGENT
                )

                user_prompt = (
                    f"Language: {language}\n"
                    f"User Question: {user_input}"
                )

                response = self.llm.invoke(
                    [
                        sys_msg,
                        HumanMessage(content=user_prompt)
                    ]
                )

                return response.content

            except Exception as e:

                print(
                    f"[BuildWiseSupervisor] "
                    f"General LLM error: {e}"
                )

        # -------------------------------------------------------------
        # Fallback response
        # -------------------------------------------------------------

        if is_bangla:

            return (
                f"**BuildWiseAI উত্তর**\n\n"
                f"আপনার প্রশ্ন: *\"{user_input}\"*\n\n"
                f"আমি আপনার নির্মাণ সম্পর্কিত প্রশ্নের উত্তর দিতে "
                f"প্রস্তুত।\n\n"
                f"বিশেষ সেবা নিতে ব্যবহার করতে পারেন:\n"
                f"- 📄 **Document Analyzer** — ব্লুপ্রিন্ট ও স্পেসিফিকেশন\n"
                f"- 🖼️ **Visual Inspector** — নির্মাণ ছবির বিশ্লেষণ\n"
                f"- 💰 **Cost Estimator** — নির্মাণ খরচের হিসাব\n"
                f"- 🔎 **Market Search** — নির্মাণ সামগ্রীর বাজার তথ্য"
            )

        return (
            f"**BuildWiseAI Assistant**\n\n"
            f"You asked: *\"{user_input}\"*\n\n"
            f"I am ready to assist with your construction, "
            f"civil engineering, and building queries.\n\n"
            f"You can also use these specialized modules:\n"
            f"- 📄 **Document Analyzer** — Blueprints and specifications\n"
            f"- 🖼️ **Visual Inspector** — Construction image analysis\n"
            f"- 💰 **Cost Estimator** — Construction cost estimation\n"
            f"- 🔎 **Market Search** — Current construction market information"
        )

    # =================================================================
    # MAIN QUERY PROCESSOR
    # =================================================================

    def process_query(
        self,
        feature: str,
        user_input: str,
        file_bytes: Optional[bytes] = None,
        file_name: Optional[str] = None,
        language: str = "English",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Main supervisor workflow.

        Flow:

        User Request
             ↓
        Router Agent
             ↓
        Specialized Agent
             ↓
        Tool / RAG / LLM
             ↓
        Final Response
        """

        extra = extra_data or {}

        # -------------------------------------------------------------
        # Router Agent
        # -------------------------------------------------------------

        route_result = router_agent.route(
            feature=feature,
            user_input=user_input
        )

        selected_agent = route_result.get(
            "agent",
            "general"
        )

        print(
            f"[BuildWiseRouter] "
            f"Feature='{feature}' → Agent='{selected_agent}'"
        )

        # =============================================================
        # 1. DOCUMENT AGENT
        # =============================================================

        if selected_agent == "document":

            return self.document_agent.process(
                file_bytes=file_bytes,
                file_name=file_name,
                user_input=user_input,
                language=language
            )

        # =============================================================
        # 2. VISION AGENT
        # =============================================================

        elif selected_agent == "vision":

            return self.vision_agent.process(
                file_bytes=file_bytes,
                file_name=file_name,
                user_input=user_input,
                language=language
            )

        # =============================================================
        # 3. COST AGENT
        # =============================================================

        elif selected_agent == "cost":

            return self.cost_agent.process(
                user_input=user_input,
                language=language,
                extra_data=extra
            )

        # =============================================================
        # 4. SEARCH AGENT
        # =============================================================

        elif selected_agent == "search":

            return self.search_agent.process(
                user_input=user_input,
                language=language
            )

        # =============================================================
        # 5. GENERAL ASSISTANT
        # =============================================================

        return self._general_chat(
            user_input=user_input,
            language=language
        )


# =====================================================================
# GLOBAL SUPERVISOR INSTANCE
# =====================================================================

agent = ConstructionAgent()
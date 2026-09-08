import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


class Settings:
    # =========================
    # GROQ
    # =========================
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )

    # =========================
    # TAVILY
    # =========================
    TAVILY_API_KEY = os.getenv(
        "TAVILY_API_KEY",
        ""
    )

    # =========================
    # LANGSMITH
    # =========================
    LANGSMITH_TRACING = os.getenv(
        "LANGSMITH_TRACING",
        "true"
    )

    LANGSMITH_ENDPOINT = os.getenv(
        "LANGSMITH_ENDPOINT",
        "https://api.smith.langchain.com"
    )

    LANGSMITH_API_KEY = os.getenv(
        "LANGSMITH_API_KEY",
        ""
    )

    LANGSMITH_PROJECT = os.getenv(
        "LANGSMITH_PROJECT",
        "Buildwise-AI"
    )

    # =========================
    # SERVER
    # =========================
    HOST = os.getenv(
        "HOST",
        "127.0.0.1"
    )

    PORT = int(
        os.getenv(
            "PORT",
            "8000"
        )
    )


# Create settings object
settings = Settings()
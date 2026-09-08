# 🏗️ BuildWise-AI — Smart AI Construction Assistant

BuildWise-AI is an AI-powered multimodal construction assistant designed to help users with common construction-related tasks such as **document analysis, visual inspection, construction cost estimation, market research, and general construction queries**.

The system combines a **multi-agent architecture, Retrieval-Augmented Generation (RAG), OCR, AI vision, web search, ChromaDB, and LangSmith tracing** to provide useful and context-aware construction assistance.

---

# ✨ Features

## 📄 1. Document Analyzer

The Document Analyzer helps users work with construction-related documents such as floor plans, drawings, and PDF files.

### Capabilities

* Upload construction drawings, floor plans, and PDF documents
* Extract text from documents using **PyMuPDF**
* Use **EasyOCR** for scanned or image-based documents
* Divide extracted information into smaller chunks
* Store document information in **ChromaDB**
* Retrieve relevant information using semantic search
* Answer questions based on uploaded documents
* Provide document-grounded responses using RAG

### Workflow

```text
Uploaded Document
       │
       ▼
  Text Extraction
  PyMuPDF / OCR
       │
       ▼
 Document Processing
       │
       ▼
   Text Chunks
       │
       ▼
     ChromaDB
       │
       ▼
Semantic Retrieval
       │
       ▼
  Document Agent
       │
       ▼
  Grounded Answer
```

---

## 🖼️ 2. Visual Inspector

The Visual Inspector allows users to upload construction-related images and receive AI-based visual observations.

### Capabilities

* Upload construction-related images
* Analyze visible building elements and conditions
* Identify possible construction or design concerns
* Provide observations and recommended actions
* Use AI vision through **Groq**
* Analyze architectural or construction-related images
* Identify situations where professional physical inspection may be required

> **Note:** The Visual Inspector provides AI-based observations and does not replace professional site inspection or engineering judgment.

### Workflow

```text
User Uploads Image
        │
        ▼
   Vision Agent
        │
        ▼
     AI Vision
        │
        ▼
 Visual Analysis
        │
        ▼
Observations & Possible Concerns
        │
        ▼
 Recommended Actions
```

---

## 💰 3. Cost Estimator

The Cost Estimator provides a preliminary construction budget based on user-provided project information.

### Inputs

* Building type
* Area per floor
* Number of floors
* Finish quality

### Capabilities

* Calculate total built-up area
* Estimate construction cost
* Provide an estimated cost breakdown
* Include contingency allowance
* Calculate estimated cost per square foot
* Provide an estimated total project budget

> **Note:** The Cost Estimator is designed for preliminary planning and budgeting. It is not a professional BOQ or quantity-surveying system.

### Workflow

```text
Building Information
        │
        ├── Building Type
        ├── Area per Floor
        ├── Number of Floors
        └── Finish Quality
                │
                ▼
        Built-up Area
                │
                ▼
        Cost Calculator
                │
                ▼
        Cost Breakdown
                │
                ▼
           Contingency
                │
                ▼
        Estimated Budget
```

---

## 🔎 4. Market Search

The Market Search feature helps users find current online information about construction materials.

### Supported Examples

* Rod / Rebar
* Cement
* Construction brands
* Material grades

### Capabilities

* Search current online construction market information
* Use **Tavily Web Search**
* Identify relevant brands and grades when available
* Extract reported prices
* Provide source information
* Display the search date
* Warn users that prices may vary by supplier, location, grade, and time

### Workflow

```text
User Query
    │
    ▼
Search Agent
    │
    ▼
Tavily Web Search
    │
    ▼
Online Sources
    │
    ▼
Relevant Information
    │
    ▼
Price / Product Extraction
    │
    ▼
Source & Date
    │
    ▼
Final Market Response
```

---

## 🤖 5. General Assistant

BuildWise-AI can answer general construction and civil engineering questions.

Examples include:

* Construction terminology
* Basic building concepts
* Material-related questions
* Construction processes
* General planning questions
* Construction-related explanations

The assistant supports:

* 🇬🇧 English
* 🇧🇩 Bangla

The language-model responses are powered by **Groq**.

---

# 🧠 Multi-Agent Architecture

BuildWise-AI uses a modular **multi-agent architecture**.

A **Router/Supervisor Agent** analyzes the user's request and selects the appropriate specialized agent.

```text
                           User
                             │
                             ▼
                    Router / Supervisor
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   Construction          Document           Vision
      Agent                Agent             Agent
          │                  │                  │
        Groq            RAG + OCR          Groq Vision
                             │
                             ▼
                          ChromaDB

          ┌──────────────────┼──────────────────┐
          │                                     │
          ▼                                     ▼
       Cost Agent                           Search Agent
          │                                     │
      Cost Tool                              Tavily
          │                                     │
          └──────────────────┬──────────────────┘
                             │
                             ▼
                       Final Response
```

---

# 🤝 AI Agents

| Agent                  | Responsibility                                            | Main Technology                 |
| ---------------------- | --------------------------------------------------------- | ------------------------------- |
| **Router Agent**       | Routes user requests to the appropriate specialized agent | Groq / LangChain                |
| **Construction Agent** | Handles general construction questions                    | Groq                            |
| **Document Agent**     | Processes documents and answers document-based questions  | RAG, ChromaDB, PyMuPDF, EasyOCR |
| **Vision Agent**       | Analyzes construction-related images                      | Groq Vision                     |
| **Cost Agent**         | Handles preliminary construction cost estimation          | Cost Calculator Tool            |
| **Search Agent**       | Searches current construction market information          | Tavily                          |

---

# 🛠️ Technology Stack

### Frontend

* **Streamlit**

### Backend

* **Python**
* **FastAPI**

### AI & LLM

* **Groq**
* **LangChain**

### Retrieval & Vector Database

* **Retrieval-Augmented Generation (RAG)**
* **ChromaDB**

### Document Processing

* **PyMuPDF**
* **EasyOCR**

### Web Search

* **Tavily**

### Observability

* **LangSmith**

---

# 📁 Project Structure

```text
BuildWise-AI-/
│
├── backend/
│   │
│   ├── agents/
│   │   ├── construction_agent.py
│   │   ├── cost_agent.py
│   │   ├── doc_agent.py
│   │   ├── router_agent.py
│   │   ├── search_agent.py
│   │   └── vision_agent.py
│
│   ├── database/
│   │   └── chroma_db/
│
│   ├── prompts/
│   │   └── construction_prompts.py
│
│   ├── retrieval/
│   │   ├── doc_loader.py
│   │   └── ocr.py
│
│   ├── tools/
│   │   ├── cost_calculator.py
│   │   ├── market_search.py
│   │   ├── rag_tool.py
│   │   └── vision_inspector.py
│
│   ├── config.py
│   ├── main.py
│   └── test_router.py
│
├── frontend/
│   ├── app.py
│   └── assets/
│       └── building.jpg
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### Folder & File Responsibilities

| Folder / File                 | Purpose                                                          |
| ----------------------------- | ---------------------------------------------------------------- |
| `backend/agents/`             | Contains the specialized AI agents and Router Agent              |
| `backend/database/chroma_db/` | Stores vector data used by the RAG system                        |
| `backend/prompts/`            | Contains AI system prompts and instructions                      |
| `backend/retrieval/`          | Handles document loading, text extraction, and OCR               |
| `backend/tools/`              | Contains cost, market search, RAG, and vision tools              |
| `backend/config.py`           | Manages application configuration and environment-based settings |
| `backend/main.py`             | FastAPI backend entry point and API endpoints                    |
| `backend/test_router.py`      | Tests Router Agent routing behavior                              |
| `frontend/app.py`             | Main Streamlit user interface                                    |
| `requirements.txt`            | Python dependencies                                              |
| `.env.example`                | Shows required environment variables without exposing secrets    |
| `.gitignore`                  | Prevents sensitive and unnecessary files from being committed    |
| `README.md`                   | Project documentation and setup guide                            |

---

# 🔄 Overall System Workflow

The overall BuildWise-AI workflow is:

```text
User
  │
  ▼
Streamlit Frontend
  │
  ▼
FastAPI Backend
  │
  ▼
Router Agent
  │
  ├──────────────┬──────────────┬──────────────┬──────────────┐
  ▼              ▼              ▼              ▼
Construction   Document       Vision         Cost
Agent          Agent          Agent          Agent
  │              │              │              │
  ▼              ▼              ▼              ▼
Groq         RAG / OCR      Groq Vision    Cost Tool
                 │
                 ▼
               ChromaDB

                          Search Agent
                              │
                              ▼
                            Tavily

  └──────────────────────┬──────────────────────┘
                         ▼
                   Final Response
                         │
                         ▼
                  Streamlit Frontend
```

### Step-by-step

1. The user submits a request through the **Streamlit frontend**.
2. The request is received by the **FastAPI backend**.
3. The **Router Agent** determines the appropriate agent.
4. The selected agent uses the required model or tool.
5. Document-related requests can use **RAG, ChromaDB, PyMuPDF, and OCR**.
6. Image-related requests use the **Vision Agent**.
7. Cost-related requests use the **Cost Calculator Tool**.
8. Market-related requests use the **Search Agent and Tavily**.
9. The system generates the final response.
10. The response is displayed to the user through the **Streamlit frontend**.

---

# 📚 Retrieval-Augmented Generation (RAG)

BuildWise-AI uses RAG to answer questions based on information from uploaded documents.

The basic process is:

```text
Document
   │
   ▼
Text Extraction
   │
   ├── PyMuPDF
   └── EasyOCR
   │
   ▼
Text Chunking
   │
   ▼
Embeddings
   │
   ▼
ChromaDB
   │
   ▼
Semantic Retrieval
   │
   ▼
Relevant Context
   │
   ▼
AI Model
   │
   ▼
Document-Grounded Response
```

RAG helps the system retrieve relevant information from uploaded construction documents before generating an answer.

---

# 👁️ Visual Inspection

The Visual Inspector uses AI vision to analyze uploaded construction-related images.

The system can provide observations about visible elements and possible concerns.

However, AI-based image analysis has limitations and cannot replace:

* Physical site inspection
* Structural engineering assessment
* Professional architectural review
* Safety inspection

For important construction or structural decisions, qualified professionals should be consulted.

---

# 💵 Cost Estimation

The Cost Estimator is designed for **preliminary project planning**.

The estimated budget depends on the information provided by the user, such as:

```text
Building Type
      +
Area per Floor
      +
Number of Floors
      +
Finish Quality
      │
      ▼
Built-up Area
      │
      ▼
Estimated Construction Cost
      │
      ▼
Contingency
      │
      ▼
Estimated Total Budget
```

Actual construction costs may vary depending on materials, labor, location, design, market conditions, and other project-specific factors.

---

# 🔎 Market Search

The Market Search Agent uses **Tavily** to retrieve current online information about construction materials.

The system attempts to provide:

* Material name
* Brand
* Grade, when available
* Reported price
* Source information
* Search date

> Online market information may change over time. Reported prices should be verified with suppliers before making purchasing decisions.

---

# 📊 LangSmith Tracing

BuildWise-AI integrates **LangSmith** for application tracing and observability.

LangSmith can help monitor and understand:

* Agent execution
* LLM calls
* Agent routing
* Tool usage
* Retrieval operations
* Overall AI workflow

This makes the application easier to monitor and debug during development.

---

# ⚙️ Requirements

Before running the project, make sure the following are installed:

* Python 3.11+
* pip
* Git
* Internet connection
* Required API keys

---

# 🚀 Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/IsmatMaksura-nb/BuildWise-AI-.git
```

Move into the project directory:

```bash
cd BuildWise-AI-
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

BuildWise-AI requires API keys for the external AI/search services used by the application.

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=BuildWise-AI
```

### Environment Variable Description

| Variable             | Purpose                                   |
| -------------------- | ----------------------------------------- |
| `GROQ_API_KEY`       | Access to Groq language and vision models |
| `TAVILY_API_KEY`     | Access to web search                      |
| `LANGSMITH_API_KEY`  | LangSmith authentication                  |
| `LANGSMITH_TRACING`  | Enables LangSmith tracing                 |
| `LANGSMITH_ENDPOINT` | LangSmith API endpoint                    |
| `LANGSMITH_PROJECT`  | LangSmith project name                    |

### 🔒 Security

**Never upload your real API keys, tokens, passwords, or credentials to GitHub.**

The `.env` file should be included in `.gitignore`.

The repository contains `.env.example` only to show which environment variables are required.

---

# ▶️ Running the Application

After completing the setup, run the Streamlit frontend from the project root:

```bash
python -m streamlit run frontend/app.py
```

Streamlit will display a local URL in the terminal.

Open that URL in a web browser to use BuildWise-AI.

---

# 🧪 Testing

The project includes a Router Agent test file:

```text
backend/test_router.py
```

The test checks different types of user requests and verifies whether they are routed to the appropriate specialized agent.

---

# ⚠️ Limitations

BuildWise-AI is an academic AI project designed for educational, informational, and preliminary planning purposes.

The system has several limitations:

* AI-generated responses may not always be completely accurate.
* Construction cost estimates are approximate.
* Online market prices can change frequently.
* Visual analysis is limited to the information visible in an uploaded image.
* Document analysis depends on the quality and readability of the uploaded document.
* AI analysis cannot replace professional site inspection.
* The system should not be used as a substitute for qualified engineers, architects, quantity surveyors, or construction professionals.

---

# 🛡️ Responsible Use

BuildWise-AI is intended to work as an **assistive construction AI system**.

For structural design, safety-critical decisions, final BOQ preparation, construction approval, or other professional decisions, users should consult an appropriately qualified professional.

---

# 🎯 Project Objectives

The main objectives of BuildWise-AI are:

1. To develop an AI-powered assistant for common construction-related queries.
2. To analyze construction documents using RAG and OCR.
3. To provide AI-assisted visual inspection.
4. To provide preliminary construction cost estimation.
5. To retrieve current construction market information using web search.
6. To demonstrate a practical multi-agent AI architecture.
7. To integrate modern AI technologies including vector databases, RAG, OCR, AI vision, web search, and LangSmith tracing.
8. To provide a simple and user-friendly interface for construction-related assistance.

---

# 📸 Screenshots

Screenshots can be added here to demonstrate the application's main interface and features.

Suggested screenshots:

* Main BuildWise-AI interface
* Document Analyzer
* Visual Inspector
* Cost Estimator
* Market Search

> The complete application and feature demonstrations are also presented in the project's demonstration video.

---

# 👩‍💻 Developer

**Developed by Ismat Maksura**

**BuildWise-AI — Final Project**

---

# 📄 Disclaimer

BuildWise-AI is developed as an academic project. The information generated by the system is intended for educational, informational, and preliminary planning purposes only.

For structural design, safety-critical decisions, final cost estimation, BOQ preparation, or actual construction work, users should consult qualified professionals.

---

# ⭐ Project Summary

**BuildWise-AI** brings together **multi-agent AI, RAG, ChromaDB, OCR, AI vision, construction cost estimation, web search, and LangSmith tracing** into a single construction-focused assistant.

The project demonstrates how modern AI technologies can be combined to create a practical and user-friendly application for the construction domain.

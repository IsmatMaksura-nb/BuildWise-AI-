# 🏗️ BuildWiseAI — AI-Powered Construction Assistant

BuildWiseAI is an AI-powered construction assistant designed to help users with common construction-related questions and tasks.

The system combines **AI agents, document analysis, OCR, RAG, ChromaDB, visual inspection, cost estimation, internet search, and LangSmith tracing** into one application.

> ⚠️ BuildWiseAI provides preliminary and informational assistance. Structural, safety-critical, code-compliance, and other important engineering decisions should always be verified by a qualified professional.

---

## 🎯 Project Overview

Construction-related information is often distributed across drawings, documents, images, material information, cost data, and online sources.

BuildWiseAI provides a single interface where users can:

* Ask general construction questions
* Analyze construction documents and blueprints
* Inspect construction images
* Estimate preliminary construction costs
* Search current construction material information

The application uses specialized AI agents and tools depending on the user's request.

---

## 👥 Target Users

BuildWiseAI is designed for:

* Students learning construction and civil engineering concepts
* Homeowners seeking preliminary construction information
* People planning small construction projects
* Users who need help understanding construction documents
* Users who need preliminary cost or material information

The system is not intended to replace professional engineers, architects, quantity surveyors, or contractors.

---

## ✨ Features

## 1. 📄 Document Analyzer

Users can upload construction documents, drawings, blueprints, or PDFs and ask questions about their contents.

The system uses:

* PyMuPDF for PDF text extraction
* EasyOCR as an OCR fallback
* Document chunking
* HuggingFace embeddings
* ChromaDB
* Retrieval-Augmented Generation (RAG)
* Groq LLM

### Example

> What is the size of the lift shown in this construction document?

The system retrieves relevant information from the uploaded document before generating the answer.

---

## 2. 🖼️ Visual Inspector

Users can upload construction images and ask questions about visible construction conditions.

The Visual Inspector can help identify:

* Visible construction elements
* Possible cracks or surface concerns
* Dampness or visible damage
* Masonry or concrete conditions
* Other visible construction observations

The system analyzes only the available visual evidence and avoids treating uncertain observations as confirmed structural defects.

---

## 3. 💰 Cost Estimator

The Cost Estimator provides a preliminary construction cost estimate based on:

* Building type
* Total area
* Number of floors
* Finish quality
* Additional notes

The estimated cost is divided into major categories such as:

* Foundation & Substructure
* Brickwork, Masonry & Plastering
* Plumbing
* Electrical Work
* Tiles, Painting & Finishing
* Labor & Supervision
* Contingency

All estimated costs are presented in BDT (৳).

> Cost results are planning-level estimates and may vary depending on location, materials, labor, design, specifications, and market conditions.

---

## 4. 🔎 Market Search

The Market Search feature retrieves current construction-related information from the internet.

It can be used for queries such as:

* Cement prices
* Rod/steel prices
* Construction material prices
* Brand-specific material information

The application uses **Tavily** as its external web search and search-grounding mechanism.

Search results are used instead of relying only on the LLM's internal knowledge.

> Market prices can change depending on location, supplier, brand, grade, quantity, and date.

---

## 5. 🤖 General Assistant

The General Assistant handles common construction-related questions.

### Examples

* What is the purpose of a foundation?
* What are the common types of foundations?
* What is RCC?
* What is the purpose of reinforcement?
* What is the difference between brickwork and concrete?

The assistant supports both **English and Bangla**.

---

# 🧠 Multi-Agent Architecture

BuildWiseAI uses a supervisor/router-based architecture.

The Router Agent determines which specialized agent should handle the user's request.

### AI Agents

| Agent              | Responsibility                               |
| ------------------ | -------------------------------------------- |
| Construction Agent | General construction assistance              |
| Router Agent       | Determines the appropriate specialized agent |
| Document Agent     | Construction document and blueprint analysis |
| Vision Agent       | Construction image inspection                |
| Cost Agent         | Preliminary construction cost estimation     |
| Search Agent       | Internet-based construction market search    |

Each agent has a specific responsibility instead of using multiple agents without a meaningful purpose.

---

# 🏗️ Technology Stack

### Frontend

* Streamlit

### Backend

* FastAPI
* Python

### AI / LLM

* Groq
* `openai/gpt-oss-20b`
* Groq Vision Model

### AI Framework

* LangChain

### Retrieval / RAG

* PyMuPDF
* EasyOCR
* HuggingFace Sentence Transformers
* ChromaDB

### Embedding Model

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### Internet Search

* Tavily

### Monitoring & Tracing

* LangSmith

---

# 📁 Project Structure

```text id="e3zdtl"
BuildWise-AI-/
│
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── construction_agent.py
│   │   ├── cost_agent.py
│   │   ├── doc_agent.py
│   │   ├── router_agent.py
│   │   ├── search_agent.py
│   │   └── vision_agent.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── chroma_db/
│   │   └── ocr_cache/
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── construction_prompts.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── doc_loader.py
│   │   └── ocr.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── cost_calculator.py
│   │   ├── market_search.py
│   │   ├── rag_tool.py
│   │   └── vision_inspector.py
│   │
│   ├── config.py
│   ├── main.py
│   └── test_router.py
│
├── frontend/
│   ├── assets/
│   │   └── building.jpg
│   ├── app.py
│   └── chat_history.json
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

The `chroma_db/` directory contains the local persistent vector database and the `ocr_cache/` directory stores cached OCR-related data. These local data directories are excluded from GitHub through `.gitignore`.

---

# 🔄 Overall Workflow

```text id="egweqs"
User Request
     ↓
Streamlit Frontend
     ↓
FastAPI Backend
     ↓
Router Agent
     ↓
Specialized Agent
     ↓
Tool / RAG / Search / Vision
     ↓
LLM Processing
     ↓
Final Response
```

Different requests follow different workflows.

### General Question

```text id="rhuz7h"
User Question
     ↓
Router Agent
     ↓
Construction Agent
     ↓
Groq LLM
     ↓
Response
```

### Document Question

```text id="5pzprl"
Document Upload
     ↓
PDF Text Extraction
     ↓
OCR Fallback if Required
     ↓
Text Chunking
     ↓
Embeddings
     ↓
ChromaDB
     ↓
Semantic Retrieval
     ↓
Relevant Context
     ↓
Groq LLM
     ↓
Grounded Response
```

### Visual Inspection

```text id="7xx0sz"
Image Upload
     ↓
Router Agent
     ↓
Vision Agent
     ↓
Groq Vision Model
     ↓
Visual Analysis
     ↓
Structured Response
```

### Cost Estimation

```text id="1idn3z"
Building Information
     ↓
Router Agent
     ↓
Cost Agent
     ↓
Cost Calculation Tool
     ↓
Preliminary Cost Breakdown
     ↓
Final Estimate
```

### Market Search

```text id="5y2nnf"
Market Query
     ↓
Router Agent
     ↓
Search Agent
     ↓
Tavily Web Search
     ↓
Relevant Search Results
     ↓
LLM Processing
     ↓
Grounded Market Information
```

---

# 📚 RAG Implementation

BuildWiseAI implements Retrieval-Augmented Generation for construction documents.

### RAG Pipeline

```text id="nj0nyt"
PDF / Construction Document
          ↓
       PyMuPDF
          ↓
    Text Extraction
          ↓
   EasyOCR if Required
          ↓
       Text Chunks
          ↓
      Embeddings
          ↓
       ChromaDB
          ↓
    Semantic Retrieval
          ↓
  Relevant Document Context
          ↓
       Groq LLM
          ↓
     Grounded Answer
```

### Chunking

The current RAG pipeline uses:

* **Chunk size:** 1000 characters
* **Chunk overlap:** 150 characters

### Embeddings

The project uses:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

This supports multilingual semantic retrieval.

### Vector Database

ChromaDB is used as the persistent vector database.

The collection used by the application is:

`buildwise_documents`

The ChromaDB data is stored locally under:

`backend/database/chroma_db/`

---

# 🔍 Document Analysis & OCR

The Document Analyzer uses PyMuPDF for extracting text from PDFs.

When a PDF contains insufficient extractable text, EasyOCR is used as a fallback for image-based or scanned content.

This allows the system to work with both text-based and image-based construction documents.

The application also follows an anti-hallucination approach:

* Document-specific answers are based on retrieved document context.
* Missing information is not invented.
* Uncertain OCR information is identified.
* General construction guidance is separated from document facts.

For example, when a requested detail is unavailable:

> Not specified in the provided document.

---

# 🖼️ Visual Inspection

The Visual Inspector uses a Groq vision model to analyze uploaded construction images.

The system focuses on visible evidence and reports:

* Visible construction elements
* Observed conditions
* Possible concerns
* Recommended next steps

The system does not treat an image alone as sufficient evidence for confirming hidden structural conditions or structural capacity.

Professional inspection is recommended for important structural or safety decisions.

---

# 💰 Cost Estimation

The Cost Estimator provides a preliminary planning estimate.

The calculation considers:

* Building type
* Area
* Number of floors
* Finish quality
* Additional notes

The Cost Agent works together with the cost calculation tool to generate an itemized estimate.

### Example Output Categories

* Foundation & Structural Works
* Brick Masonry & Plaster
* Plumbing
* Electrical
* Tiles / Painting / Finishing
* Labor / Site Supervision
* Contingency
* Total Estimated Cost

The result is presented as an estimate rather than an exact professional BOQ.

---

# 🌐 Internet Search & Grounding

BuildWiseAI uses Tavily for external web search.

This is mainly used for construction market information where current data is important.

### Search Workflow

```text id="qgmomr"
User Query
     ↓
Search Agent
     ↓
Tavily Search
     ↓
Relevant Web Results
     ↓
Result Processing
     ↓
Grounded Response
```

The system includes source information and a warning that market prices may vary over time and between suppliers.

---

# 📊 LangSmith Tracing

BuildWiseAI is integrated with LangSmith for tracing and monitoring.

Important application workflows can be inspected through LangSmith.

Tracing covers important parts of the system such as:

* User requests
* Agents
* LLM execution
* Tools
* Retrieval
* Search
* Final response generation

### Example Trace Categories

#### General Assistant

Shows the general AI workflow.

#### Document Analyzer

Shows document analysis and RAG-related execution.

#### Visual Inspector

Shows the visual inspection workflow.

#### Cost Estimator

Shows cost agent execution.

#### Market Search

Shows internet search execution.

These traces help demonstrate how the different components of BuildWiseAI work together.

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

### Example

```text id="zav7co"
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
GROQ_VISION_MODEL=qwen/qwen3.6-27b

TAVILY_API_KEY=

HOST=127.0.0.1
PORT=8000

CHROMA_PERSIST_DIR=./backend/database/chroma_db

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT="Buildwise-AI"

GEMINI_API_KEY=
GEMINI_SEARCH_MODEL=gemini-3.5-flash-lite
```

### Security

API keys and credentials must not be committed to GitHub.

The project uses:

* `.env` for local secrets
* `.env.example` to show the required environment variables

The `.env` file is included in `.gitignore`.

---

# 📦 Installation

## Clone the Repository

```text id="edy5u6"
git clone https://github.com/IsmatMaksura-nb/BuildWise-AI-.git
```

## Move into the Project Directory

```text id="bwnfp2"
cd BuildWise-AI-
```

## Create a Virtual Environment

```text id="xvc57b"
python -m venv venv
```

## Activate the Virtual Environment on Windows

```text id="wyrzzn"
venv\Scripts\activate
```

## Install Dependencies

```text id="c6s81h"
pip install -r requirements.txt
```

Create the `.env` file and add the required API keys.

---

# ▶️ Running the Application

## Start the Backend

From the project root:

```text id="r97yuj"
uvicorn backend.main:app --reload
```

The FastAPI backend will run at:

```text id="igbwf9"
http://127.0.0.1:8000
```

## Start the Frontend

Open another terminal and run:

```text id="32jvjt"
python -m streamlit run frontend/app.py
```

The Streamlit application will then open in the browser.

---

# 🧪 Testing

The project includes a router test file:

```text id="qf8cmi"
backend/test_router.py
```

The router is tested with different feature types, including:

* General
* Document
* Visual
* Cost
* Market

The tests verify that requests are routed to the appropriate specialized agent.

---

# ⚠️ Limitations & Responsible Use

BuildWiseAI is an AI-assisted construction information system.

It should not be used as a replacement for:

* Structural engineers
* Architects
* Quantity surveyors
* Contractors
* Building inspectors
* Other qualified professionals

### Important Limitations

* Cost estimates are preliminary.
* Market prices can change over time.
* Image analysis is limited to visible evidence.
* OCR may contain errors.
* Uploaded documents may not contain all required information.
* AI-generated responses may require professional verification.
* Building-code and safety-critical decisions should be verified using appropriate professional and official sources.

---

# 🎯 Project Objectives

The main objectives of BuildWiseAI are to:

* Build a practical real-world AI application.
* Demonstrate an agent-based architecture.
* Integrate multiple specialized agents.
* Implement RAG using construction documents.
* Use a vector database for semantic retrieval.
* Integrate OCR for scanned/image-based documents.
* Provide construction image analysis.
* Provide preliminary construction cost estimation.
* Retrieve current market information through internet search.
* Demonstrate search-grounded responses.
* Monitor AI workflows using LangSmith.
* Provide a useful and understandable construction assistant.

---

## 🎥 Project Demonstration

### Part 1 — Application Demonstration & Codebase Explanation

**YouTube Demo:** [https://youtu.be/JZd3dqFTaxQ](https://youtu.be/JZd3dqFTaxQ)

The video first demonstrates BuildWiseAI from the user's perspective and then explains the backend, architecture, and codebase of the application.

#### Application Demonstration

The demonstration covers the main implemented features:

- **General Assistant** — Answers general construction-related questions
- **Document Analyzer** — Analyzes uploaded construction documents and floor plans
- **Visual Inspector** — Analyzes uploaded building images
- **Cost Estimator** — Provides preliminary construction cost estimates
- **Market Search** — Searches for current construction material and market information

The demonstration shows how users interact with these features through the Streamlit interface, including realistic queries and document or image uploads where applicable.

#### Backend & Codebase Explanation

After demonstrating the application, the video explains how the system is implemented, including:

- Project architecture and folder structure
- Streamlit frontend
- FastAPI backend
- Router Agent and specialized agents
- Agent workflow and tool execution
- LLM and model configuration
- Prompt design
- Cost calculation
- Internet/market search
- OCR and document processing
- RAG pipeline
- HuggingFace embeddings
- ChromaDB vector database
- Visual inspection workflow
- Important functions and their roles
- LangSmith integration
- Environment variables and configuration

The overall system workflow is also explained:

**User → Streamlit Frontend → FastAPI Backend → Router Agent → Selected Agent → Tool / RAG / OCR / Internet Search → Language Model → Final Answer**

The video focuses on both the working application and how the major backend components work together to provide construction-related assistance.

### Part 2 — LangSmith Tracing

Public LangSmith traces demonstrating the main BuildWiseAI workflows:

**General Assistant:**  
https://smith.langchain.com/public/28be6e2e-ccdd-45a7-b3ba-cf06c7c4392b/r/01a06c60-bc85-7443-9860-2369269241ef?start_time=2026-09-04T12%3A24%3A34.181599Z

**Document / RAG:**  
https://smith.langchain.com/public/5749b3dc-af97-4dca-a68c-fb39c80d043a/r/01a06c66-0132-7291-bf00-30ecc829392d?start_time=2026-09-04T12%3A30%3A19.436108Z

**Visual Inspection:**  
https://smith.langchain.com/public/b63d0791-3197-4dcb-9914-bb4e2fbce738/r/01a06c77-c013-7e80-b3ff-16271d11ad1a?start_time=2026-09-04T12%3A49%3A42.419789Z

**Cost Estimation:**  
https://smith.langchain.com/public/7de4344f-45f0-4070-9e64-0f22c0df4981/r/01a06d6e-a121-7893-96d4-8ebd5e9377d6?start_time=2026-09-04T17%3A19%3A21.889985Z

**Market Search:**  
https://smith.langchain.com/public/f0c15bdb-b985-41b7-a716-e2e420755c90/r/01a070b4-1b28-7ac0-bb30-8934b6564720?start_time=2026-09-05T08%3A34%3A06.760438Z
# 👩‍💻 Developer

**Ismat Maksura**

BuildWiseAI was developed as a final project demonstrating the practical integration of modern AI technologies into a real-world construction-related application.

---

# ⚠️ Disclaimer

BuildWiseAI provides AI-generated informational and preliminary assistance.

The system does not replace professional engineering, architectural, inspection, quantity surveying, or construction services.

For structural, safety-critical, code-compliance, or other important project decisions, consult a qualified professional.

---

# ⭐ Summary

BuildWiseAI combines:

**AI Agents + Router + RAG + ChromaDB + OCR + Vision + Cost Estimation + Internet Search + Search Grounding + LangSmith**

to provide an integrated AI-powered construction assistance system.

**Problem → User → Workflow → AI → Useful Outcome**

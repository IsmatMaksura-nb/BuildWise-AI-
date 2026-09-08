🏗️ BuildWise-AI — Smart AI Construction Assistant

BuildWise-AI is an AI-powered construction assistant designed to help users with common construction-related tasks such as document analysis, visual inspection, construction cost estimation, market research, and general construction queries.

The system combines a multi-agent architecture, Retrieval-Augmented Generation (RAG), OCR, AI vision, web search, ChromaDB, and LangSmith tracing.

✨ Features
📄 1. Document Analyzer

The Document Analyzer helps users analyze construction-related documents such as floor plans, drawings, and PDF files.

Capabilities:

Upload construction drawings, floor plans, and PDF documents
Extract text using PyMuPDF
Use EasyOCR for scanned or image-based documents
Split extracted text into chunks
Generate embeddings
Store document information in ChromaDB
Retrieve relevant information using semantic search
Generate document-grounded answers using RAG

Workflow:

Uploaded Document
       ↓
Text Extraction
(PyMuPDF / EasyOCR)
       ↓
Text Processing
       ↓
Text Chunking
       ↓
Embeddings
       ↓
ChromaDB
       ↓
Semantic Retrieval
       ↓
Document Agent
       ↓
Grounded Answer
🖼️ 2. Visual Inspector

The Visual Inspector allows users to upload construction-related images and receive AI-based visual observations.

Capabilities:

Upload construction images
Analyze visible building elements
Identify possible construction or design concerns
Provide observations and recommendations
Use AI vision through Groq
Support construction-related image analysis

The Visual Inspector provides AI-based observations and does not replace professional site inspection or engineering judgment.

💰 3. Cost Estimator

The Cost Estimator provides a preliminary construction budget based on user-provided project information.

Inputs:

Building type
Area per floor
Number of floors
Finish quality

Capabilities:

Calculate total built-up area
Estimate construction cost
Provide cost breakdown
Include contingency
Calculate estimated cost per square foot
Provide estimated total project budget

Cost estimates are for preliminary planning only and may vary depending on materials, labor, location, design, and market conditions.

🔎 4. Market Search

The Market Search feature helps users find current online information about construction materials.

Examples:

Rod / Rebar
Cement
Construction brands
Material grades

Capabilities:

Search current online construction information
Use Tavily Web Search
Identify relevant brands and grades
Extract reported prices
Provide source information
Display search date
Mention that prices may vary by supplier, location, grade, and time
🤖 5. General Assistant

The General Assistant answers common construction-related questions.

Examples include:

Construction terminology
Basic building concepts
Material-related questions
Construction processes
General planning questions

The assistant supports:

English
Bangla
🧠 Multi-Agent Architecture

BuildWise-AI uses a modular multi-agent architecture.

A Router/Supervisor Agent analyzes the user's request and selects the appropriate specialized agent.

                         User
                           ↓
                  Router / Supervisor
                           ↓
       ┌───────────┬───────────┬───────────┐
       ↓           ↓           ↓           ↓
 Construction  Document     Vision      Cost
    Agent       Agent        Agent       Agent
       ↓           ↓           ↓           ↓
     Groq      RAG + OCR   Groq Vision  Cost Tool
                   ↓
                ChromaDB

                    ↓
               Search Agent
                    ↓
                  Tavily

                    ↓
             Final Response
                    ↓
             Streamlit UI
🤝 AI Agents
Agent	Responsibility	Technology
Router Agent	Routes requests to the appropriate agent	LangChain / Groq
Construction Agent	Handles general construction questions	Groq
Document Agent	Processes construction documents	RAG / ChromaDB / OCR
Vision Agent	Analyzes construction images	Groq Vision
Cost Agent	Estimates preliminary construction costs	Cost Calculator
Search Agent	Searches construction market information	Tavily
🛠️ Technology Stack
Frontend
Streamlit
Backend
Python
FastAPI
AI & LLM
Groq
LangChain
Retrieval
Retrieval-Augmented Generation (RAG)
ChromaDB
HuggingFace Embeddings
Document Processing
PyMuPDF
EasyOCR
Web Search
Tavily
Observability
LangSmith
📁 Project Structure
BuildWise-AI-/
│
├── backend/
│   ├── agents/
│   │   ├── construction_agent.py
│   │   ├── cost_agent.py
│   │   ├── doc_agent.py
│   │   ├── router_agent.py
│   │   ├── search_agent.py
│   │   └── vision_agent.py
│   │
│   ├── database/
│   │   └── chroma_db/
│   │
│   ├── prompts/
│   │   └── construction_prompts.py
│   │
│   ├── retrieval/
│   │   ├── doc_loader.py
│   │   └── ocr.py
│   │
│   ├── tools/
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
│   ├── app.py
│   ├── chat_history.json
│   └── assets/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
🔄 Overall Workflow
User
 ↓
Streamlit Frontend
 ↓
FastAPI Backend
 ↓
Router Agent
 ↓
Specialized Agent
 ↓
Required Tool / Model
 ↓
Processing
 ↓
Final Response
 ↓
Streamlit Frontend

Depending on the request, the system can use:

General Construction Agent → Groq
Document Agent → RAG + OCR + ChromaDB
Vision Agent → Groq Vision
Cost Agent → Cost Calculator
Search Agent → Tavily
📚 RAG Workflow

BuildWise-AI uses RAG to answer questions based on uploaded construction documents.

Document
   ↓
Text Extraction
   ↓
PyMuPDF / EasyOCR
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
Document-Grounded Answer

This allows the system to retrieve relevant information from uploaded documents before generating an answer.

👁️ Visual Inspection

The Visual Inspector uses AI vision to analyze uploaded construction-related images.

The system can provide observations about visible building elements and possible concerns.

For important structural or safety decisions, users should consult qualified professionals.

💵 Cost Estimation

The Cost Estimator provides preliminary construction cost estimates based on:

Building Type
      +
Area per Floor
      +
Number of Floors
      +
Finish Quality
      ↓
Built-up Area
      ↓
Cost Calculation
      ↓
Cost Breakdown
      ↓
Contingency
      ↓
Estimated Total Cost

The results are intended for preliminary planning and should not be treated as a professional BOQ.

🔎 Market Search

The Market Search Agent uses Tavily to retrieve current online construction market information.

The system attempts to provide:

Material name
Brand
Grade
Reported price
Source
Search date

Market prices can change depending on supplier, location, brand, grade, and time.

📊 LangSmith Tracing

BuildWise-AI integrates LangSmith for tracing and monitoring AI workflows.

LangSmith helps monitor:

Agent execution
LLM calls
Agent routing
Tool usage
Retrieval operations
Final responses

This makes the system easier to monitor, debug, and evaluate.

⚙️ Requirements

Before running the project, install:

Python 3.11+
pip
Git
Required API keys
Internet connection
🚀 Installation & Setup
1. Clone the Repository
git clone https://github.com/IsmatMaksura-nb/BuildWise-AI-.git
cd BuildWise-AI-
2. Create Virtual Environment
python -m venv venv
Windows
venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
🔐 Environment Variables

Create a .env file in the project root.

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
Environment Variables
Variable	Purpose
GROQ_API_KEY	Groq API access
GROQ_MODEL	Groq language model
GROQ_VISION_MODEL	Groq vision model
TAVILY_API_KEY	Web search access
HOST	Backend host
PORT	Backend port
CHROMA_PERSIST_DIR	ChromaDB storage location
LANGSMITH_TRACING	Enables LangSmith tracing
LANGSMITH_ENDPOINT	LangSmith API endpoint
LANGSMITH_API_KEY	LangSmith authentication
LANGSMITH_PROJECT	LangSmith project name
GEMINI_API_KEY	Gemini API access
GEMINI_SEARCH_MODEL	Gemini search model

Gemini variables are included in the environment configuration and are only required if the corresponding Gemini functionality is used.

🔒 Security

Never upload real API keys or credentials to GitHub.

The .env file is excluded using .gitignore.

Only .env.example is included in the repository.

▶️ Running the Application

From the project root:

python -m streamlit run frontend/app.py

Then open the local Streamlit URL shown in the terminal.

🧪 Testing

The project includes Router Agent tests:

backend/test_router.py

The tests verify that different types of user requests are routed to the appropriate specialized agents.

⚠️ Limitations & Responsible Use

BuildWise-AI is an academic project intended for educational, informational, and preliminary planning purposes.

The system has several limitations:

AI-generated responses may not always be completely accurate.
Construction cost estimates are approximate.
Online market prices may change frequently.
Visual analysis depends on the uploaded image.
Document analysis depends on document quality.
OCR results may contain errors.
AI analysis cannot replace professional site inspection.
The system should not replace qualified engineers, architects, or construction professionals.

For structural design, safety-critical decisions, final BOQ preparation, or actual construction work, users should consult qualified professionals.

🎯 Project Objectives
Develop an AI-powered assistant for construction-related queries.
Analyze construction documents using RAG and OCR.
Provide AI-assisted visual inspection.
Provide preliminary construction cost estimation.
Retrieve current construction market information using web search.
Demonstrate a practical multi-agent AI architecture.
Integrate RAG, vector databases, OCR, AI vision, web search, and LangSmith.
Provide a simple and user-friendly construction assistance system.
📸 Screenshots

Screenshots are optional. The application's main features and workflow are demonstrated in the project presentation video.

👩‍💻 Developer

Ismat Maksura

BuildWise-AI — Final Project

📄 Disclaimer

BuildWise-AI is developed as an academic project. The information generated by the system is intended for educational, informational, and preliminary planning purposes only.

For structural design, safety-critical decisions, final cost estimation, BOQ preparation, or actual construction work, users should consult qualified professionals.

⭐ Project Summary

BuildWise-AI combines multi-agent AI, RAG, ChromaDB, OCR, AI vision, construction cost estimation, web search, and LangSmith tracing into one construction-focused AI assistant.

The project demonstrates how modern AI technologies can be integrated to build a practical and user-friendly application for the construction domain.

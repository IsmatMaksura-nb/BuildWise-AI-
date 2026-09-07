# 🏗️ BuildWise-AI — Smart AI Construction Assistant

BuildWise-AI is an AI-powered multi-modal construction assistant designed to help users with common construction-related tasks such as document analysis, visual inspection, construction cost estimation, market research, and general construction queries.

The system combines a **multi-agent architecture, Retrieval-Augmented Generation (RAG), OCR, web search, AI vision, and LangSmith tracing** to provide useful and context-aware construction assistance.

---

## ✨ Features

### 📄 Document Analyzer

- Upload construction drawings, floor plans, and PDF documents
- Extract text from documents using PyMuPDF
- Use EasyOCR for scanned or image-based documents
- Store extracted document information in ChromaDB
- Retrieve relevant information using semantic search
- Answer questions based on the uploaded document
- Reduce unsupported answers using document-grounded responses

### 🖼️ Visual Inspector

- Upload construction-related images
- Analyze visible building elements and conditions
- Identify possible construction or design concerns
- Provide observations and recommended actions
- Uses AI vision through Groq
- Identifies limitations when an image is a rendering or when physical inspection is required

### 💰 Cost Estimator

- Estimate construction costs based on:
  - Building type
  - Area per floor
  - Number of floors
  - Finish quality
- Calculate total built-up area
- Provide an estimated cost breakdown
- Include contingency allowance
- Provide estimated total project budget
- Provide estimated cost per square foot
- Designed for planning-level estimation, not professional BOQ preparation

### 🔎 Market Search

- Search current construction material market information
- Supports construction materials such as rod and cement
- Detect relevant brands and grades when applicable
- Uses Tavily web search to retrieve current online information
- Extract and validate reported prices
- Provide source information
- Display the search date
- Warn users that market prices may vary by supplier, location, grade, and time

### 🤖 General Construction Assistant

- Answer general construction and civil engineering questions
- Provide construction-related explanations and guidance
- Support English and Bangla responses
- Uses Groq-powered language models

---

## 🧠 Multi-Agent Architecture

BuildWise-AI uses a modular multi-agent architecture where a Router/Supervisor determines which specialized agent should handle the user's request.

```text
                         User
                           │
                           ▼
                  Router / Supervisor
                           │
        ┌──────────┬──────┼──────┬──────────┐
        ▼          ▼      ▼      ▼          ▼
 Construction  Document Vision  Cost      Search
    Agent       Agent   Agent   Agent       Agent
       │          │       │       │           │
      Groq      OCR +   Groq    Cost        Tavily
                RAG     Vision   Tool        Search
                 │
            ChromaDB
                 │
                 ▼
           Final Response
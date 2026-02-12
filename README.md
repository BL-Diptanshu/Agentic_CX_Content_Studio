# 🎨 Agentic CX Content Studio

Agentic CX Content Studio is an advanced AI-powered application designed to orchestrate and generate high-quality marketing campaigns. By leveraging **multi-agent systems (CrewAI)**, **LLMs (Groq, Gemini)**, and **RAG (Retrieval Augmented Generation)**, it ensures that all generated content aligns perfectly with your brand's voice and guidelines.

## 🚀 Features

-   **Campaign Orchestration**: Uses a team of AI agents (Planner, Content Generator, Brand Validator) to create comprehensive campaigns.
-   **Brand Consistency (RAG)**: Upload your brand guidelines (PDF, DOCX, TXT) to enforce tone, style, and terminology using vector search (FAISS).
-   **Multi-Modal Generation**:
    -   **Copywriting**: Generates engaging marketing copy, social media posts, and emails.
    -   **Image Generation**: Creates on-brand visuals using Flux/Stable Diffusion via Replicate/HuggingFace APIs.
-   **Interactive UI**: A user-friendly Streamlit interface for campaign creation, management, and review.
-   **Document Parsing**: Automatically extracts campaign details from uploaded briefs.
-   **PDF Export**: Download fully formatted campaign reports as PDFs.
-   **Auto-Regeneration**: Agents self-correct and regenerate content if it fails brand validation.

## 🛠️ Tech Stack

-   **Frontend**: [Streamlit](https://streamlit.io/)
-   **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
-   **Orchestration**: [CrewAI](https://crewai.com/)
-   **LLMs**: Groq (Llama 3), Google Gemini
-   **Vector DB**: FAISS (Facebook AI Similarity Search)
-   **Database**: PostgreSQL / SQLite (managed via SQLAlchemy)
-   **Image Gen**: Replicate / HuggingFace
-   **Utilities**: `python-docx`, `PyPDF2`, `ReportLab`

## 📂 Project Structure

```
Agentic_CX_Content_Studio/
├── config/                 # Configuration files (logging, agents)
├── data/                   # Data storage
├── docs/                   # Documentation
├── src/
│   ├── core/               # Core logic (Agents, Orchestrator, Database)
│   ├── processing/         # Document parsing and processing
│   ├── routes/             # FastAPI routes
│   └── utils/              # Helper functions (PDF generation, branding)
├── static/                 # Static assets (generated images)
├── main.py                 # Backend entry point (FastAPI)
├── streamlit.py            # Frontend entry point (Streamlit)
├── requirements.txt        # Python dependencies
└── ...
```

## ⚡ Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Agentic_CX_Content_Studio
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables**:
    Create a `.env` file in the root directory and add your API keys:
    ```env
    GROQ_API_KEY=your_groq_key
    GOOGLE_API_KEY=your_google_key
    REPLICATE_API_TOKEN=your_replicate_token
    # Add other necessary keys
    ```

5.  **Run the Application**:

    **Backend (FastAPI)**:
    ```bash
    uvicorn main:app --reload
    ```

    **Frontend (Streamlit)**:
    Open a new terminal and run:
    ```bash
    streamlit run streamlit.py
    ```

## 📖 Usage

1.  Open the Streamlit app in your browser (usually `http://localhost:8501`).
2.  **Create Campaign**:
    -   **Manual**: Enter campaign name, brand, objective, and audience.
    -   **Upload**: Upload a brief (DOCX/PDF) to auto-fill details.
3.  **Generate**: Click "Create Campaign". The agents will plan, write, and validate content.
4.  **Review**: View the generated text and image.
5.  **Regenerate**: If the result isn't perfect, click "Regenerate" to try again with feedback.
6.  **Export**: Click "Save as PDF" to download the campaign assets.

## 🔗 API Endpoints

The backend exposes several endpoints via FastAPI (available at `http://localhost:8000/docs`):

-   `POST /api/v1/orchestrate/campaign`: Start full campaign generation.
-   `POST /api/v1/generate/text`: Generate text with LLM.
-   `POST /api/v1/generate/image`: Generate images.
-   `POST /api/v1/validate/text`: Validate content against brand rules.
-   `GET /api/v1/campaigns/{id}`: Retrieve campaign details.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## 📄 License

[MIT License](LICENSE)

# PDF Intelligence & Collaboration System

A Django web application for uploading PDFs, generating AI summaries, asking grounded questions about documents, sharing PDFs through unique links, and collaborating through comments.

## Features
- Secure signup/login using Django's password hashing
- PDF-only upload validation and 20 MB size limit
- Owner-only dashboard and protected document access
- Automatic PDF text extraction with PyPDF2
- AI-generated 3-5 sentence summary using Google Gemini
- Filename search
- Unique shareable links for guest viewing
- Guest and owner comments
- Conversational AI chat retaining the latest 5 user/assistant turns
- Long PDF handling using overlapping chunks and lexical relevance ranking
- API keys stored server-side in environment variables

## AI approach
After upload, text is extracted and sent to Gemini with a constrained summarization prompt requiring a concise, factual 3-5 sentence summary. For chat, the PDF is split into overlapping chunks. The chunks most relevant to the user's question are selected and supplied with recent conversation history. The prompt explicitly instructs the model not to invent facts and to state when the document does not contain the answer.

## Local setup
```bash
git clone <your-repository-url>
cd pdf_intelligence_collab
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your Gemini key:
```env
SECRET_KEY=your-secret
DEBUG=True
GEMINI_API_KEY=your-key
```

Then:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

## Deployment
Use PostgreSQL for production, configure `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`, and `GEMINI_API_KEY` in the deployment platform's environment-variable settings. Run migrations before starting the application.

## Security notes
Passwords are hashed by Django and never stored as plaintext. Gemini keys remain server-side. Documents are checked before owner-only access; shared documents require the unique token URL.

## Scope trade-off
The assignment's must-have features are implemented. Semantic embeddings, threaded comments, email notifications, password reset, and streaming responses are intentionally left as good-to-have extensions.

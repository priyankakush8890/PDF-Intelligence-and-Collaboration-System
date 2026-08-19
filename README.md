# PDF Intelligence & Collaboration System

An AI-powered PDF intelligence and collaboration platform built with Django. Users can upload PDFs, generate AI summaries, ask questions grounded in the document, search documents semantically, share PDFs with others, collaborate through comments and replies, and receive email invitations.

This project was developed as part of the **SpotDraft AI Engineering Intern Take-Home Assignment**.

---

## 🚀 Features

### 🔐 Authentication

- User registration
- Login and logout
- Password reset and account recovery
- Protected user dashboard
- Users can access only their own uploaded PDFs

---

### 📄 PDF Management

- Upload PDF documents
- PDF validation
- Maximum upload size validation
- Extract text from uploaded PDFs
- View uploaded PDFs
- AI-generated summary for each PDF
- Document ownership and access control

---

### 🤖 AI PDF Intelligence

The application uses **Google Gemini** for AI-powered document understanding.

#### AI Summary

After uploading a PDF:

1. Text is extracted from the PDF.
2. Relevant document content is sent to the LLM.
3. Gemini generates a concise summary.

The summary focuses on:

- Document purpose
- Important facts
- Key obligations
- Important entities or dates
- Major conclusions

The AI is instructed not to invent information.

---

### 💬 Grounded AI Chat

Users can ask questions about an uploaded PDF.

The application:

1. Splits the PDF text into chunks.
2. Finds the most relevant chunks for the user's question.
3. Sends only the relevant PDF context to the LLM.
4. Includes recent conversation history for follow-up questions.
5. Instructs the model to answer strictly from the provided document context.

If the answer is not present in the document, the AI is instructed to clearly state that the document does not provide that information.

---

### ⚡ Streaming AI Responses

AI responses are streamed to the chat interface instead of waiting for the complete response.

This provides a more interactive, real-time chat experience.

---

### 🔎 Semantic PDF Search

The dashboard supports both:

- Filename-based search
- Embedding-based semantic search

For semantic search:

1. PDF text is divided into overlapping chunks.
2. Each chunk is converted into an embedding using Gemini.
3. Embeddings are stored in the database.
4. The search query is also converted into an embedding.
5. Cosine similarity is used to find the most relevant document chunks.
6. Documents are ranked based on their best matching chunk.

This allows users to find PDFs based on their meaning rather than only their filename.

For example, searching for:

> employment contract

can find a document even if its filename is:

> Agreement_v3.pdf

---

### 🔗 PDF Sharing

Users can share PDFs using a unique share link.

Features include:

- Unique UUID-based share tokens
- Copy share link functionality
- Shared PDF access
- Access control for document owners
- Secure PDF file access using share tokens

---

### 📧 Email Notifications

Users can share a PDF through email.

The recipient receives an email containing:

- The sender's username
- The PDF title
- A link to access the shared PDF

For local development, Django's console email backend can be used. For production, an SMTP email provider can be configured using environment variables.

---

### 💬 Collaboration and Comments

Users can collaborate on shared documents using comments.

Features include:

- Logged-in user comments
- Guest comments on shared documents
- Comment author display
- Timestamp for comments
- Threaded replies to existing comments

---

### ✍️ Rich Text Comments

Comments support basic text formatting:

- **Bold text**
- *Italic text*
- Bullet points

User input is sanitized before rendering to help prevent unsafe HTML.

---

🛠 Tech Stack
Backend
Python
Django
AI
Google Gemini API
Gemini Flash
Gemini Embeddings
PDF Processing
PyPDF2
Semantic Search
Gemini Embeddings
NumPy
Cosine Similarity
Database
SQLite
Frontend
Django Templates
HTML
CSS
JavaScript
Bootstrap
Other Libraries
Bleach
python-dotenv
